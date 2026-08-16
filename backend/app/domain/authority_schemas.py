"""
CivicPulse AI — Authority & Routing Schemas.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum
from app.domain.enums import ComplaintStatus

class Jurisdiction(BaseModel):
    """
    Geographic or logical scope of authority.
    For MVP, uses identifier-based mapping.
    """
    id: Optional[str] = None
    jurisdiction_id: str
    name: str
    level: str  # e.g., "ward", "city", "state"

class Department(BaseModel):
    id: Optional[str] = None
    department_id: str
    name: str
    jurisdictions: List[str]  # List of jurisdiction_ids
    active: bool = True

class RoutingRule(BaseModel):
    id: Optional[str] = None
    category: str
    jurisdiction: Optional[str] = None  # None implies fallback/global
    department_id: str
    priority: int = 1
    active: bool = True

class AuthorityActionType(str, Enum):
    ROUTED = "routed"
    ASSIGNED = "assigned"
    STATUS_UPDATE = "status_update"
    NOTE_ADDED = "note_added"

class AuthorityActionHistory(BaseModel):
    """Immutable audit trail for authority actions."""
    id: Optional[str] = None
    complaint_id: str
    actor_id: str
    action_type: AuthorityActionType
    previous_status: Optional[ComplaintStatus] = None
    new_status: Optional[ComplaintStatus] = None
    note: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class RoutingResult(BaseModel):
    status: str  # "success", "ambiguous", "unavailable"
    department_id: Optional[str] = None
    explanation: str

class ComplaintAssignment(BaseModel):
    id: Optional[str] = None
    complaint_id: str
    department_id: str
    assigned_authority_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class IntegrationStatus(str, Enum):
    NOT_CONFIGURED = "not_configured"
    READY = "ready"
    SENT = "sent"
    ACKNOWLEDGED = "acknowledged"
    FAILED = "failed"

class ExternalIntegrationDelivery(BaseModel):
    id: Optional[str] = None
    complaint_id: str
    integration_id: str
    provider: str
    status: IntegrationStatus
    external_reference: Optional[str] = None
    error_reason: Optional[str] = None
    request_timestamp: datetime = Field(default_factory=datetime.utcnow)
    response_timestamp: Optional[datetime] = None
