"""
CivicPulse AI — Dashboard Service.
"""

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from pymongo.asynchronous.database import AsyncDatabase

from app.domain.dashboard_schemas import (
    DashboardSummaryResponse, 
    StatusCount, 
    CategoryCount, 
    TrendPoint,
    GeoJSONFeatureCollection,
    GeoJSONFeature,
    GeoJSONPoint,
    GeoJSONFeatureProperties
)
from app.domain.enums import AIAnalysisStatus

class DashboardService:
    def __init__(self, db: AsyncDatabase):
        self.db = db

    def _build_match_query(
        self, 
        user_id: str, 
        status: Optional[str] = None, 
        category: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """Build a secure MongoDB match query restricting to the authenticated user."""
        query: Dict[str, Any] = {"user_id": user_id}
        if status:
            query["status"] = status
        if category:
            query["category"] = category
            
        date_query = {}
        if date_from:
            try:
                date_query["$gte"] = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            except ValueError:
                pass
        if date_to:
            try:
                date_query["$lte"] = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
            except ValueError:
                pass
        if date_query:
            query["created_at"] = date_query
            
        return query

    async def get_summary(
        self, 
        user_id: str,
        status: Optional[str] = None, 
        category: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> DashboardSummaryResponse:
        
        match_stage = {"$match": self._build_match_query(user_id, status, category, date_from, date_to)}
        
        # 1. Total Complaints & Evidence Stats
        # We can run parallel pipelines using $facet
        pipeline = [
            match_stage,
            {
                "$facet": {
                    "totals": [
                        {
                            "$group": {
                                "_id": None,
                                "total": {"$sum": 1},
                                "with_evidence": {"$sum": {"$cond": [{"$gt": ["$evidence_count", 0]}, 1, 0]}}
                            }
                        }
                    ],
                    "by_status": [
                        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
                    ],
                    "by_category": [
                        {"$group": {"_id": "$category", "count": {"$sum": 1}}}
                    ],
                    "trend": [
                        {
                            "$group": {
                                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                                "count": {"$sum": 1}
                            }
                        },
                        {"$sort": {"_id": 1}}
                    ]
                }
            }
        ]
        
        cursor = await self.db["complaints"].aggregate(pipeline)
        result = await cursor.to_list(length=1)
        data = result[0] if result else {}
        
        totals = data.get("totals", [])
        total_complaints = totals[0]["total"] if totals else 0
        with_evidence = totals[0]["with_evidence"] if totals else 0
        
        status_counts = [StatusCount(status=item["_id"], count=item["count"]) for item in data.get("by_status", [])]
        category_counts = [CategoryCount(category=item["_id"], count=item["count"]) for item in data.get("by_category", [])]
        trend = [TrendPoint(date=item["_id"], count=item["count"]) for item in data.get("trend", [])]
        
        # 2. AI Stats
        # First, find all complaint IDs that match the filter
        # If filters are applied, we only want AI stats for those complaints
        complaint_cursor = self.db["complaints"].find(match_stage["$match"], {"_id": 1})
        complaint_ids = [str(doc["_id"]) for doc in await complaint_cursor.to_list(length=None)]
        
        ai_stats = {"completed": 0, "processing": 0, "failed": 0, "pending": 0}
        if complaint_ids:
            ai_pipeline = [
                {"$match": {"complaint_id": {"$in": complaint_ids}}},
                {"$group": {"_id": "$status", "count": {"$sum": 1}}}
            ]
            ai_cursor = await self.db["ai_analyses"].aggregate(ai_pipeline)
            ai_results = await ai_cursor.to_list(length=None)
            for item in ai_results:
                status_val = str(item["_id"]).lower()
                if status_val in ai_stats:
                    ai_stats[status_val] = item["count"]
                else:
                    ai_stats[status_val] = item["count"]
        
        return DashboardSummaryResponse(
            total_complaints=total_complaints,
            status_counts=status_counts,
            category_counts=category_counts,
            trend=trend,
            complaints_with_evidence=with_evidence,
            ai_stats=ai_stats
        )

    async def get_map_data(
        self, 
        user_id: str,
        status: Optional[str] = None, 
        category: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> GeoJSONFeatureCollection:
        
        query = self._build_match_query(user_id, status, category, date_from, date_to)
        
        # Ensure we only fetch complaints that actually have location data
        query["location.geo"] = {"$exists": True}
        
        cursor = self.db["complaints"].find(query).limit(1000) # Soft limit to prevent map crash
        
        features = []
        for doc in await cursor.to_list(length=None):
            location = doc.get("location", {})
            geo = location.get("geo", {})
            coords = geo.get("coordinates")
            
            if coords and len(coords) == 2:
                features.append(GeoJSONFeature(
                    geometry=GeoJSONPoint(coordinates=coords),
                    properties=GeoJSONFeatureProperties(
                        id=str(doc["_id"]),
                        title=doc.get("title", ""),
                        category=doc.get("category", ""),
                        status=doc.get("status", ""),
                        created_at=doc.get("created_at").isoformat() if doc.get("created_at") else ""
                    )
                ))
                
        return GeoJSONFeatureCollection(features=features)
