"""
CivicPulse AI — Authority & Admin Dashboard API Schemas.

Domain models for authority queue, operational metrics, complaint details,
filtering, sorting, and pagination.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.domain.authority_schemas import AuthorityActionHistory, IntegrationStatus
from app.domain.enums import CivicCategory, ComplaintStatus


class AuthorityComplaintListItem(BaseModel):
    """Summarized complaint item for authority queue."""
    id: str = Field(alias="_id")
    title: str
    description: str
    category: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    user_id: str
    evidence_count: int = 0
    assigned_authority_id: Optional[str] = None
    department_id: Optional[str] = None
    priority_score: Optional[float] = None
    location_summary: Optional[str] = None

    class Config:
        populate_by_name = True


class AuthorityQueueResponse(BaseModel):
    """Paginated list of authority complaints."""
    items: List[Dict[str, Any]]
    total: int
    page: int
    page_size: int
    total_pages: int


class StatusCount(BaseModel):
    status: str
    count: int


class CategoryCount(BaseModel):
    category: str
    count: int


class AuthorityDashboardSummary(BaseModel):
    """Operational summary metrics for authority & admin users."""
    total_complaints: int
    unassigned_count: int
    assigned_to_me_count: int
    in_progress_count: int
    resolved_count: int
    closed_count: int
    status_counts: List[StatusCount]
    category_counts: List[CategoryCount]
    recent_audit_activity: List[Dict[str, Any]]
    integration_status: Dict[str, int]
    scope_note: str


class AuthorityComplaintDetailResponse(BaseModel):
    """Enriched operational view of a complaint for authority users."""
    complaint: Dict[str, Any]
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    ai_analysis: List[Dict[str, Any]] = Field(default_factory=list)
    assignment: Optional[Dict[str, Any]] = None
    status_history: List[Dict[str, Any]] = Field(default_factory=list)
    audit_trail: List[Dict[str, Any]] = Field(default_factory=list)
    routing_info: Optional[Dict[str, Any]] = None
    intelligence: Optional[Dict[str, Any]] = None
    external_delivery: Optional[Dict[str, Any]] = None
