"""
CivicPulse AI — Intelligence Schemas.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

class RelationType(str, Enum):
    DUPLICATE = "duplicate"
    RELATED = "related"
    INDEPENDENT = "independent"
    INSUFFICIENT_DATA = "insufficient_data"

class ComplaintRelation(BaseModel):
    """Represents a computed semantic/geographic relation between two complaints."""
    id: Optional[str] = None
    complaint_a_id: str
    complaint_b_id: str
    relation_type: RelationType
    semantic_similarity: float
    geographic_distance_meters: Optional[float] = None
    category_match: bool
    temporal_distance_days: float
    match_score: float
    explanation: str
    algorithm_version: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class IncidentCluster(BaseModel):
    """Groups related complaints into a civic incident."""
    id: Optional[str] = None
    cluster_id: str  # Unique logical identifier
    member_complaint_ids: List[str]
    clustering_algorithm: str
    clustering_version: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class IntelligenceResponse(BaseModel):
    """API Response for a complaint's intelligence status."""
    complaint_id: str
    relations: List[ComplaintRelation]
    cluster: Optional[IncidentCluster] = None
    
class EmbeddingDocument(BaseModel):
    """Persistence model for Complaint Embeddings."""
    complaint_id: str
    embedding: List[float]
    model_name: str
    model_version: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
