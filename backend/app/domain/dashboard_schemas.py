"""
CivicPulse AI — Dashboard Schemas.
"""

from typing import Dict, List, Any
from pydantic import BaseModel

class StatusCount(BaseModel):
    status: str
    count: int

class CategoryCount(BaseModel):
    category: str
    count: int

class TrendPoint(BaseModel):
    date: str
    count: int

class DashboardSummaryResponse(BaseModel):
    """Aggregate statistics for the dashboard."""
    total_complaints: int
    status_counts: List[StatusCount]
    category_counts: List[CategoryCount]
    trend: List[TrendPoint]
    complaints_with_evidence: int
    ai_stats: Dict[str, int]  # e.g., {"completed": 5, "processing": 1, "failed": 0}

class GeoJSONPoint(BaseModel):
    type: str = "Point"
    coordinates: List[float]

class GeoJSONFeatureProperties(BaseModel):
    id: str
    title: str
    category: str
    status: str
    created_at: str

class GeoJSONFeature(BaseModel):
    type: str = "Feature"
    geometry: GeoJSONPoint
    properties: GeoJSONFeatureProperties

class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[GeoJSONFeature]
