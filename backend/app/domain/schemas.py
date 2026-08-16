"""
CivicPulse AI — Domain Schemas.

Pydantic models defining the structure of MongoDB documents.
These are persistence-layer schemas — NOT API request/response schemas.

Separation of concerns:
    - These schemas define what gets stored in MongoDB.
    - API schemas (request/response) will be defined separately in later phases.
    - Repositories use these for document validation on read/write.

Design decisions documented in docs/02-database/data-modeling-decisions.md.

SECURITY:
    - Password hashes are NEVER included here. Phase 3 will handle auth.
    - No secrets in schema defaults.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from app.domain.enums import (
    AIAnalysisStatus,
    AssignmentStatus,
    CivicCategory,
    ComplaintStatus,
    DepartmentStatus,
    EvidenceProcessingStatus,
    NotificationStatus,
    NotificationType,
    PredictionStatus,
    PredictionType,
    UserRole,
    UserStatus,
)


def _utcnow() -> datetime:
    """Return current UTC datetime. Centralized for consistency."""
    return datetime.now(timezone.utc)


# ============================================================
# Location (embedded document)
# ============================================================

class GeoJSONPoint(BaseModel):
    """
    GeoJSON Point for MongoDB 2dsphere indexing.

    Embedded within complaint documents.

    Decision: Embedded (not referenced).
    Reason: Location is owned by and always accessed with the complaint.
    It has no independent lifecycle and is immutable after submission.
    Embedding avoids a join for every spatial query.
    """

    type: str = Field(default="Point", description="GeoJSON type. Always 'Point'.")
    coordinates: List[float] = Field(
        ...,
        min_length=2,
        max_length=2,
        description="[longitude, latitude]. Longitude first per GeoJSON spec.",
    )

    @field_validator("type")
    @classmethod
    def type_must_be_point(cls, v: str) -> str:
        if v != "Point":
            raise ValueError("GeoJSON type must be 'Point'.")
        return v

    @field_validator("coordinates")
    @classmethod
    def validate_coordinates(cls, v: List[float]) -> List[float]:
        if len(v) != 2:
            raise ValueError("Coordinates must be [longitude, latitude].")
        longitude, latitude = v
        if not (-180 <= longitude <= 180):
            raise ValueError(
                f"Longitude must be between -180 and 180, got {longitude}."
            )
        if not (-90 <= latitude <= 90):
            raise ValueError(
                f"Latitude must be between -90 and 90, got {latitude}."
            )
        return v


class LocationData(BaseModel):
    """
    Location information for a complaint.

    Embedded within complaint documents.
    Contains both structured GeoJSON (for indexing) and optional
    human-readable address information.
    """

    geo: GeoJSONPoint = Field(
        ..., description="GeoJSON point for geospatial queries."
    )
    address: Optional[str] = Field(
        default=None, max_length=500, description="Human-readable address."
    )
    locality: Optional[str] = Field(
        default=None, max_length=200, description="Locality/area name."
    )
    city: Optional[str] = Field(
        default=None, max_length=100, description="City name."
    )
    pincode: Optional[str] = Field(
        default=None, max_length=20, description="Postal/pin code."
    )


# ============================================================
# User
# ============================================================

class UserDocument(BaseModel):
    """
    User persistence schema.

    Collection: users
    Unique constraint: email (case-insensitive via normalized_email)

    Note: No password field. Phase 3 (Authentication) will determine
    the auth mechanism (password hash, OAuth, etc.) and extend this
    schema accordingly.
    """

    password_hash: Optional[str] = Field(
        default=None, description="Password hash (bcrypt). None for Google OAuth users."
    )
    google_sub: Optional[str] = Field(
        default=None,
        description="Google subject identifier (stable, immutable Google user ID). "
                    "None for password-only accounts.",
    )
    profile_picture_url: Optional[str] = Field(
        default=None,
        description="Google profile picture URL. Informational only.",
    )
    email: str = Field(
        ..., max_length=254, description="User email address."
    )
    normalized_email: str = Field(
        ..., max_length=254,
        description="Lowercase email for unique index. Application must set this.",
    )
    display_name: str = Field(
        ..., min_length=1, max_length=100, description="Display name."
    )
    role: UserRole = Field(
        default=UserRole.CITIZEN, description="User role."
    )
    department_id: Optional[str] = Field(
        default=None,
        description="Department reference (for authority users only).",
    )
    status: UserStatus = Field(
        default=UserStatus.ACTIVE, description="Account status."
    )
    created_at: datetime = Field(
        default_factory=_utcnow, description="Account creation timestamp (UTC)."
    )
    updated_at: datetime = Field(
        default_factory=_utcnow, description="Last update timestamp (UTC)."
    )

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        """Basic email format check. Full validation belongs to auth phase."""
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email format.")
        return v.strip()

    @field_validator("normalized_email")
    @classmethod
    def validate_normalized_email(cls, v: str) -> str:
        if v != v.lower():
            raise ValueError("normalized_email must be lowercase.")
        return v


# ============================================================
# Department
# ============================================================

class DepartmentDocument(BaseModel):
    """
    Department persistence schema.

    Collection: departments

    Departments are real database entities, not hardcoded.
    The exact department list is managed through the application,
    not baked into source code.
    """

    name: str = Field(
        ..., min_length=1, max_length=200, description="Department name."
    )
    code: str = Field(
        ..., min_length=1, max_length=50,
        description="Short code for the department (e.g. 'PWD', 'WATER').",
    )
    description: Optional[str] = Field(
        default=None, max_length=1000, description="Department description."
    )
    status: DepartmentStatus = Field(
        default=DepartmentStatus.ACTIVE, description="Operational status."
    )
    created_at: datetime = Field(
        default_factory=_utcnow, description="Creation timestamp (UTC)."
    )
    updated_at: datetime = Field(
        default_factory=_utcnow, description="Last update timestamp (UTC)."
    )


# ============================================================
# Complaint
# ============================================================

class ComplaintDocument(BaseModel):
    """
    Complaint persistence schema.

    Collection: complaints

    This is the central domain object of CivicPulse.

    Embedded:
        - location (LocationData): Always accessed with complaint, immutable.

    Referenced (by ID string):
        - user_id → users: Author changes rarely; complaint queries don't
          always need full user data.
        - department_id → departments: Assignment can change; separate lifecycle.
        - cluster_id → incident_clusters: Cluster membership is computed
          and can change.

    Evidence and AI analysis are stored in separate collections
    (referenced by complaint_id) because:
        - Evidence: Multiple per complaint, potentially large metadata,
          independent processing lifecycle.
        - AI Analysis: Multiple runs possible, independent status,
          should not bloat the complaint document.
    """

    user_id: str = Field(
        ..., description="Reference to the submitting user (_id as string)."
    )
    title: str = Field(
        ..., min_length=5, max_length=300, description="Complaint title."
    )
    description: str = Field(
        ..., min_length=10, max_length=5000, description="Detailed description."
    )
    category: CivicCategory = Field(
        ..., description="Civic problem category."
    )
    location: LocationData = Field(
        ..., description="Location of the civic problem."
    )
    status: ComplaintStatus = Field(
        default=ComplaintStatus.SUBMITTED, description="Current lifecycle status."
    )
    priority_score: Optional[float] = Field(
        default=None, ge=0, le=100,
        description="Computed priority score (0-100). Set by priority engine.",
    )
    department_id: Optional[str] = Field(
        default=None, description="Assigned department reference."
    )
    cluster_id: Optional[str] = Field(
        default=None, description="Incident cluster reference."
    )
    ai_analysis_id: Optional[str] = Field(
        default=None, description="Latest AI analysis reference."
    )
    evidence_count: int = Field(
        default=0, ge=0,
        description="Count of attached evidence items. "
                    "Denormalized for display; authoritative count from evidence collection.",
    )
    created_at: datetime = Field(
        default_factory=_utcnow, description="Submission timestamp (UTC)."
    )
    updated_at: datetime = Field(
        default_factory=_utcnow, description="Last update timestamp (UTC)."
    )


# ============================================================
# Evidence
# ============================================================

class EvidenceDocument(BaseModel):
    """
    Evidence persistence schema.

    Collection: evidence

    Referenced by complaint_id. Separate collection because:
    - Multiple evidence items per complaint.
    - Each has its own processing lifecycle.
    - Storage metadata can be large.
    - Independent processing status.
    """

    complaint_id: str = Field(
        ..., description="Reference to the parent complaint."
    )
    user_id: str = Field(
        ..., description="Reference to the uploading user."
    )
    storage_key: str = Field(
        ..., max_length=500,
        description="Storage reference key (bucket path, not filesystem path).",
    )
    original_filename: str = Field(
        ..., max_length=255, description="Original uploaded filename."
    )
    mime_type: str = Field(
        ..., max_length=100, description="MIME type of the evidence."
    )
    size_bytes: int = Field(
        ..., ge=0, description="File size in bytes."
    )
    processing_status: EvidenceProcessingStatus = Field(
        default=EvidenceProcessingStatus.PENDING,
        description="Processing pipeline status.",
    )
    created_at: datetime = Field(
        default_factory=_utcnow, description="Upload timestamp (UTC)."
    )


# ============================================================
# AI Analysis
# ============================================================

class AIAnalysisDocument(BaseModel):
    """
    AI Analysis persistence schema.

    Collection: ai_analyses

    Stores validated AI analysis results for a complaint.
    Separate collection because:
    - Multiple analysis runs possible (retries, version upgrades).
    - Independent processing lifecycle and status.
    - Should not bloat complaint documents.
    - Allows querying analysis results independently.
    """

    complaint_id: str = Field(
        ..., description="Reference to the analyzed complaint."
    )
    pipeline_version: str = Field(
        ..., max_length=50, description="Analysis pipeline version identifier."
    )
    provider: str = Field(
        ..., max_length=50, description="AI provider (e.g. 'groq', 'ollama')."
    )
    model: str = Field(
        ..., max_length=100, description="Model identifier used."
    )
    status: AIAnalysisStatus = Field(
        default=AIAnalysisStatus.PENDING, description="Analysis status."
    )
    result: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Structured analysis result (validated before storage).",
    )
    confidence: Optional[float] = Field(
        default=None, ge=0, le=1,
        description="Overall confidence score (0-1) if applicable.",
    )
    created_at: datetime = Field(
        default_factory=_utcnow, description="Analysis creation timestamp (UTC)."
    )
    completed_at: Optional[datetime] = Field(
        default=None, description="Analysis completion timestamp (UTC)."
    )
    error_message: Optional[str] = Field(
        default=None, max_length=1000,
        description="Error details if analysis failed (no secrets).",
    )


# ============================================================
# Incident Cluster
# ============================================================

class IncidentClusterDocument(BaseModel):
    """
    Incident Cluster persistence schema.

    Collection: incident_clusters

    Groups geographically/semantically related complaints.

    Decision: complaint_ids stored as array reference list.
    complaint_count is denormalized for efficient dashboard queries.
    The authoritative member list is complaint_ids; complaint_count
    should be updated transactionally with membership changes.
    """

    category: Optional[CivicCategory] = Field(
        default=None, description="Cluster category if homogeneous."
    )
    complaint_ids: List[str] = Field(
        default_factory=list,
        description="References to member complaints.",
    )
    complaint_count: int = Field(
        default=0, ge=0,
        description="Denormalized count. Updated with membership changes.",
    )
    representative_location: Optional[GeoJSONPoint] = Field(
        default=None,
        description="Centroid/representative location for the cluster.",
    )
    radius_meters: Optional[float] = Field(
        default=None, ge=0,
        description="Approximate radius of the cluster in meters.",
    )
    algorithm_version: Optional[str] = Field(
        default=None, max_length=50,
        description="Algorithm/version that created this cluster.",
    )
    created_at: datetime = Field(
        default_factory=_utcnow, description="Cluster creation timestamp (UTC)."
    )
    updated_at: datetime = Field(
        default_factory=_utcnow, description="Last update timestamp (UTC)."
    )


# ============================================================
# Assignment
# ============================================================

class AssignmentDocument(BaseModel):
    """
    Assignment persistence schema.

    Collection: assignments

    Tracks authority assignment of complaints to departments/users.
    Separate collection because:
    - Assignment history matters (reassignments).
    - Independent lifecycle from the complaint itself.
    """

    complaint_id: str = Field(
        ..., description="Reference to the assigned complaint."
    )
    department_id: str = Field(
        ..., description="Reference to the assigned department."
    )
    assigned_to: Optional[str] = Field(
        default=None, description="Reference to specific assigned user."
    )
    assigned_by: str = Field(
        ..., description="Reference to the user who made the assignment."
    )
    status: AssignmentStatus = Field(
        default=AssignmentStatus.ACTIVE, description="Assignment status."
    )
    assigned_at: datetime = Field(
        default_factory=_utcnow, description="Assignment timestamp (UTC)."
    )
    updated_at: datetime = Field(
        default_factory=_utcnow, description="Last update timestamp (UTC)."
    )


# ============================================================
# Status History
# ============================================================

class StatusHistoryDocument(BaseModel):
    """
    Status History persistence schema.

    Collection: status_history

    Records every complaint status transition for traceability.
    Separate collection because:
    - Append-only audit trail.
    - Unbounded growth (many transitions per complaint).
    - Queried independently for timeline views.
    """

    complaint_id: str = Field(
        ..., description="Reference to the complaint."
    )
    previous_status: Optional[ComplaintStatus] = Field(
        default=None, description="Status before transition (None for initial)."
    )
    new_status: ComplaintStatus = Field(
        ..., description="Status after transition."
    )
    actor_id: Optional[str] = Field(
        default=None, description="User who triggered the transition."
    )
    reason: Optional[str] = Field(
        default=None, max_length=1000,
        description="Reason or comment for the transition.",
    )
    created_at: datetime = Field(
        default_factory=_utcnow, description="Transition timestamp (UTC)."
    )






# ============================================================
# Audit Log
# ============================================================

class AuditLogDocument(BaseModel):
    """
    Audit Log persistence schema.

    Collection: audit_logs

    Records critical actions for auditability.
    Append-only. Never stores secrets.
    """

    actor_id: Optional[str] = Field(
        default=None, description="User who performed the action (None for system)."
    )
    action: str = Field(
        ..., max_length=100, description="Action identifier (e.g. 'complaint.created')."
    )
    resource_type: str = Field(
        ..., max_length=50, description="Type of affected resource."
    )
    resource_id: str = Field(
        ..., description="ID of affected resource."
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional context (no secrets).",
    )
    created_at: datetime = Field(
        default_factory=_utcnow, description="Action timestamp (UTC)."
    )
