"""
CivicPulse AI — Intelligence Service.
Handles Complaint normalization, semantic embeddings, candidate similarity matching, and incident clustering.
"""

import logging
import asyncio
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
import math

from pymongo.asynchronous.database import AsyncDatabase
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from app.config import get_settings
from app.domain.intelligence_schemas import (
    RelationType, ComplaintRelation, IncidentCluster, EmbeddingDocument
)
from app.repositories.collections import ComplaintRepository

logger = logging.getLogger("civicpulse.intelligence")

# We cache the model to prevent reloading it into memory repeatedly
_embedding_model = None

def get_model(model_name: str) -> SentenceTransformer:
    global _embedding_model
    if _embedding_model is None:
        logger.info(f"Loading SentenceTransformer model {model_name}...")
        _embedding_model = SentenceTransformer(model_name)
    return _embedding_model

def haversine_distance(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """Calculate the great circle distance in meters between two points on the earth."""
    # Convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])

    # Haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    r = 6371000 # Radius of earth in meters.
    return c * r

class IntelligenceService:
    def __init__(self, db: AsyncDatabase):
        self.db = db
        self.settings = get_settings()
        self.complaint_repo = ComplaintRepository(db)
        
    async def process_intelligence(self, complaint_id: str) -> None:
        """
        End-to-end intelligence pipeline for a single complaint.
        Idempotent design.
        """
        logger.info(f"Starting intelligence processing for complaint {complaint_id}")
        
        # 1. Fetch Complaint
        complaint = await self.complaint_repo.find_by_id(complaint_id)
        if not complaint:
            logger.error(f"Complaint {complaint_id} not found for intelligence processing.")
            return

        # 2. Get or Create Embedding
        embedding_doc = await self._get_or_create_embedding(complaint_id, complaint)
        if not embedding_doc:
            logger.error("Failed to generate embedding.")
            return
            
        # 3. Retrieve Candidates
        candidates = await self._get_candidates(complaint)
        
        # 4. Evaluate Similarity & Relations
        relations_created = False
        for candidate in candidates:
            # Prevent self-match
            if str(candidate["_id"]) == complaint_id:
                continue
                
            # Canonical ordering to prevent duplicate relation directions
            comp_a, comp_b = sorted([complaint_id, str(candidate["_id"])])
            
            # Skip if relation already evaluated for this version
            existing_relation = await self.db["complaint_relations"].find_one({
                "complaint_a_id": comp_a,
                "complaint_b_id": comp_b,
                "algorithm_version": self.settings.embedding_version
            })
            if existing_relation:
                continue
                
            relation = await self._evaluate_relation(complaint_id, complaint, embedding_doc, str(candidate["_id"]), candidate)
            if relation:
                await self.db["complaint_relations"].insert_one(relation.model_dump(exclude={"id"}))
                relations_created = True
                
        # 5. Recompute Clustering
        if relations_created:
            await self._recompute_clusters()

    async def _get_or_create_embedding(self, complaint_id: str, complaint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        # Check existing
        existing = await self.db["complaint_embeddings"].find_one({
            "complaint_id": complaint_id,
            "model_version": self.settings.embedding_version
        })
        if existing:
            return existing
            
        # Normalize text
        title = complaint.get("title", "").strip()
        description = complaint.get("description", "").strip()
        category = complaint.get("category", "")
        
        # We append category to text to provide strong semantic signal
        text = f"[{category}] {title}. {description}"
        
        # Generate embedding
        try:
            model = get_model(self.settings.embedding_model)
            # Encode and convert to native python float list
            vector = model.encode(text).tolist()
            
            doc = EmbeddingDocument(
                complaint_id=complaint_id,
                embedding=vector,
                model_name=self.settings.embedding_model,
                model_version=self.settings.embedding_version
            )
            
            doc_dict = doc.model_dump()
            await self.db["complaint_embeddings"].insert_one(doc_dict)
            return doc_dict
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return None

    async def _get_candidates(self, complaint: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        We use Geographic filtering as the primary candidate generator to avoid O(N^2) global vector search.
        If MongoDB Vector Search was available, we'd use `$vectorSearch`.
        """
        location = complaint.get("location", {})
        coords = location.get("geo", {}).get("coordinates")
        
        if not coords or len(coords) != 2:
            return [] # Cannot match geographically without coords
            
        # MongoDB 2dsphere $near
        # Max distance from config
        pipeline = [
            {
                "$geoNear": {
                    "near": { "type": "Point", "coordinates": coords },
                    "distanceField": "dist.calculated",
                    "maxDistance": self.settings.geo_candidate_radius_meters,
                    "spherical": True
                }
            },
            {"$limit": self.settings.candidate_search_limit}
        ]
        
        cursor = await self.db["complaints"].aggregate(pipeline)
        return await cursor.to_list(length=None)

    async def _evaluate_relation(
        self, 
        base_id: str, base_comp: Dict[str, Any], base_emb: Dict[str, Any], 
        candidate_id: str, candidate_comp: Dict[str, Any]
    ) -> Optional[ComplaintRelation]:
        
        # Canonical order
        comp_a, comp_b = sorted([base_id, candidate_id])
        
        # Get candidate embedding
        candidate_emb_doc = await self.db["complaint_embeddings"].find_one({
            "complaint_id": candidate_id,
            "model_version": self.settings.embedding_version
        })
        
        if not candidate_emb_doc:
            # We skip evaluation until candidate is embedded
            return None
            
        vec_base = np.array(base_emb["embedding"]).reshape(1, -1)
        vec_cand = np.array(candidate_emb_doc["embedding"]).reshape(1, -1)
        
        semantic_sim = float(cosine_similarity(vec_base, vec_cand)[0][0])
        
        # Geographic
        base_coords = base_comp.get("location", {}).get("geo", {}).get("coordinates")
        cand_coords = candidate_comp.get("location", {}).get("geo", {}).get("coordinates")
        geo_dist = None
        if base_coords and cand_coords:
            geo_dist = haversine_distance(base_coords[0], base_coords[1], cand_coords[0], cand_coords[1])
            
        # Category
        cat_match = base_comp.get("category") == candidate_comp.get("category")
        
        # Temporal
        t1 = base_comp.get("created_at")
        t2 = candidate_comp.get("created_at")
        temp_dist = 0.0
        if t1 and t2:
            if isinstance(t1, str): t1 = datetime.fromisoformat(t1.replace('Z', '+00:00'))
            if isinstance(t2, str): t2 = datetime.fromisoformat(t2.replace('Z', '+00:00'))
            temp_dist = abs((t1 - t2).total_seconds()) / (24 * 3600)
            
        # Classification Heuristic
        # Heuristic rules:
        # If semantic > duplicate threshold AND geo < 200m -> DUPLICATE
        # If semantic > related threshold AND geo < max -> RELATED
        # Else INDEPENDENT
        
        relation_type = RelationType.INDEPENDENT
        explanation = "Independent complaints."
        
        if semantic_sim >= self.settings.duplicate_similarity_threshold:
            if geo_dist is not None and geo_dist <= 200:
                relation_type = RelationType.DUPLICATE
                explanation = "High semantic similarity and very close geographic proximity."
            else:
                relation_type = RelationType.RELATED
                explanation = "High semantic similarity but distinct geographic locations."
        elif semantic_sim >= self.settings.related_similarity_threshold:
            if geo_dist is not None and geo_dist <= self.settings.geo_candidate_radius_meters:
                relation_type = RelationType.RELATED
                explanation = "Moderate semantic similarity within neighborhood."

        if temp_dist > self.settings.temporal_proximity_days:
            relation_type = RelationType.INDEPENDENT
            explanation = "Temporal distance exceeds relation bounds."
            
        return ComplaintRelation(
            complaint_a_id=comp_a,
            complaint_b_id=comp_b,
            relation_type=relation_type,
            semantic_similarity=semantic_sim,
            geographic_distance_meters=geo_dist,
            category_match=cat_match,
            temporal_distance_days=temp_dist,
            match_score=semantic_sim,
            explanation=explanation,
            algorithm_version=self.settings.embedding_version
        )

    async def _recompute_clusters(self) -> None:
        """
        Graph Connected Components clustering.
        Nodes = Complaints
        Edges = Relations (Type == DUPLICATE or RELATED)
        """
        # Fetch all positive relations for current version
        cursor = self.db["complaint_relations"].find({
            "algorithm_version": self.settings.embedding_version,
            "relation_type": {"$in": [RelationType.DUPLICATE.value, RelationType.RELATED.value]}
        })
        
        adj_list = {}
        for rel in await cursor.to_list(length=None):
            a = rel["complaint_a_id"]
            b = rel["complaint_b_id"]
            if a not in adj_list: adj_list[a] = []
            if b not in adj_list: adj_list[b] = []
            adj_list[a].append(b)
            adj_list[b].append(a)
            
        visited = set()
        clusters = []
        
        for node in adj_list:
            if node not in visited:
                component = []
                stack = [node]
                while stack:
                    curr = stack.pop()
                    if curr not in visited:
                        visited.add(curr)
                        component.append(curr)
                        stack.extend(adj_list.get(curr, []))
                
                if len(component) > 1:
                    clusters.append(sorted(component))
                    
        # Replace existing clusters safely
        await self.db["incident_clusters"].delete_many({"clustering_version": self.settings.clustering_version})
        
        for idx, comp_list in enumerate(clusters):
            # Deterministic cluster ID based on the minimum complaint ID
            cluster_id = f"CLUSTER-{comp_list[0][:8]}"
            cluster = IncidentCluster(
                cluster_id=cluster_id,
                member_complaint_ids=comp_list,
                clustering_algorithm=self.settings.clustering_algorithm,
                clustering_version=self.settings.clustering_version
            )
            await self.db["incident_clusters"].insert_one(cluster.model_dump(exclude={"id"}))

    async def get_intelligence_for_complaint(self, complaint_id: str) -> Dict[str, Any]:
        """Fetch relations and cluster membership for a complaint."""
        # Relations
        cursor = self.db["complaint_relations"].find({
            "$or": [{"complaint_a_id": complaint_id}, {"complaint_b_id": complaint_id}],
            "algorithm_version": self.settings.embedding_version
        })
        relations = await cursor.to_list(length=None)
        
        # Convert relations to model to ensure schema conformance
        parsed_relations = []
        for r in relations:
            r["id"] = str(r["_id"])
            parsed_relations.append(ComplaintRelation(**r).model_dump())
            
        # Cluster
        cluster_doc = await self.db["incident_clusters"].find_one({
            "member_complaint_ids": complaint_id,
            "clustering_version": self.settings.clustering_version
        })
        
        parsed_cluster = None
        if cluster_doc:
            cluster_doc["id"] = str(cluster_doc["_id"])
            parsed_cluster = IncidentCluster(**cluster_doc).model_dump()
            
        return {
            "complaint_id": complaint_id,
            "relations": parsed_relations,
            "cluster": parsed_cluster
        }
