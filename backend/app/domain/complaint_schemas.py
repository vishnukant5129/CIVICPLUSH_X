"""
CivicPulse AI — API Schemas for Complaints.

These are the public API request/response schemas, distinct from the
internal database domain schemas (app/domain/schemas.py).
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.domain.enums import CivicCategory, ComplaintStatus
from app.domain.schemas import LocationData


class ComplaintCreateRequest(BaseModel):
    """Payload for creating a new civic complaint."""
    title: str = Field(..., min_length=5, max_length=300)
    description: str = Field(..., min_length=10, max_length=5000)
    category: CivicCategory = Field(...)
    location: LocationData = Field(...)


class ComplaintResponse(BaseModel):
    """Safe public representation of a complaint."""
    id: str
    user_id: str
    title: str
    description: str
    category: CivicCategory
    location: LocationData
    status: ComplaintStatus
    priority_score: Optional[float] = None
    department_id: Optional[str] = None
    cluster_id: Optional[str] = None
    evidence_count: int
    created_at: datetime
    updated_at: datetime


class StatusHistoryResponse(BaseModel):
    """Safe public representation of status history."""
    id: str
    complaint_id: str
    previous_status: Optional[ComplaintStatus]
    new_status: ComplaintStatus
    actor_id: Optional[str]
    reason: Optional[str]
    created_at: datetime
