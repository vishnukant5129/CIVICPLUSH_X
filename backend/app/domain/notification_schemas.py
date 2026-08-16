"""
CivicPulse AI — Domain Schemas for Events, Notifications, Preferences & Deliveries.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Domain event classifications."""

    COMPLAINT_CREATED = "complaint_created"
    COMPLAINT_ROUTED = "complaint_routed"
    COMPLAINT_ASSIGNED = "complaint_assigned"
    COMPLAINT_STATUS_CHANGED = "complaint_status_changed"
    COMPLAINT_RESOLVED = "complaint_resolved"
    COMPLAINT_CLOSED = "complaint_closed"
    AI_ANALYSIS_COMPLETED = "ai_analysis_completed"


class DomainEvent(BaseModel):
    """Immutable record of a domain event."""

    id: Optional[str] = Field(default=None, alias="_id")
    event_id: str
    event_type: EventType
    complaint_id: Optional[str] = None
    actor_id: Optional[str] = None
    previous_state: Optional[str] = None
    new_state: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


class NotificationType(str, Enum):
    """Taxonomy of user-facing notifications."""

    COMPLAINT_SUBMITTED = "complaint_submitted"
    COMPLAINT_ROUTED = "complaint_routed"
    COMPLAINT_ASSIGNED = "complaint_assigned"
    STATUS_UPDATE = "status_update"
    AI_ANALYSIS_COMPLETED = "ai_analysis_completed"
    SYSTEM = "system"


class NotificationDocument(BaseModel):
    """In-app persistent notification document."""

    id: Optional[str] = Field(default=None, alias="_id")
    notification_id: str
    user_id: str
    event_id: Optional[str] = None
    complaint_id: Optional[str] = None
    type: NotificationType
    title: str
    body: str
    read_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        populate_by_name = True


class NotificationResponse(BaseModel):
    """Public API representation of a notification."""

    id: str
    user_id: str
    event_id: Optional[str] = None
    complaint_id: Optional[str] = None
    type: NotificationType
    title: str
    body: str
    read: bool
    read_at: Optional[datetime] = None
    created_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)


class NotificationPreferences(BaseModel):
    """User preferences for notification delivery channels."""

    user_id: str
    in_app_enabled: bool = True
    email_enabled: bool = False
    sms_enabled: bool = False
    push_enabled: bool = False
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DeliveryChannel(str, Enum):
    """Delivery channel types."""

    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


class DeliveryStatus(str, Enum):
    """Delivery state tracking."""

    PERSISTED = "persisted"
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    NOT_CONFIGURED = "not_configured"


class DeliveryRecord(BaseModel):
    """Execution audit record for external or internal delivery channel."""

    id: Optional[str] = Field(default=None, alias="_id")
    notification_id: str
    channel: DeliveryChannel
    provider: str
    status: DeliveryStatus
    attempted_at: datetime = Field(default_factory=datetime.utcnow)
    provider_message_id: Optional[str] = None
    error_reason: Optional[str] = None

    class Config:
        populate_by_name = True
