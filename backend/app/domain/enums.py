"""
CivicPulse AI — Centralized Domain Enums.

All status values, roles, and categorized constants used across
the CivicPulse domain are defined here.

These are the single source of truth. Do NOT scatter string
literals for these values throughout the codebase.
"""

from __future__ import annotations

from enum import Enum


# --- User ---

class UserRole(str, Enum):
    """Roles a user can hold in the CivicPulse system."""

    CITIZEN = "citizen"
    AUTHORITY = "authority"
    ADMIN = "admin"


class UserStatus(str, Enum):
    """Account status for a user."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


# --- Department ---

class DepartmentStatus(str, Enum):
    """Operational status of a department."""

    ACTIVE = "active"
    INACTIVE = "inactive"


# --- Complaint ---

class ComplaintStatus(str, Enum):
    """
    Complaint lifecycle statuses.

    Primary flow:
        SUBMITTED → UNDER_REVIEW → VERIFIED → ASSIGNED → IN_PROGRESS → RESOLVED → CLOSED

    Alternate outcomes:
        REJECTED, DUPLICATE, INVALID
    """

    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    VERIFIED = "verified"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

    # Alternate outcomes
    REJECTED = "rejected"
    DUPLICATE = "duplicate"
    INVALID = "invalid"


class CivicCategory(str, Enum):
    """
    Controlled civic problem categories.

    Decision: Application-controlled enum (not database-backed entities).

    Reason: The PRD defines a fixed initial category set for AI classification.
    Categories are structural to the AI pipeline and complaint routing logic.
    Adding a new category requires code changes to classification prompts
    and routing rules, so database-backed dynamic categories would create
    a false sense of flexibility without actual runtime benefit in MVP.

    If post-MVP requirements demand user-defined categories, a migration
    to database-backed entities can be performed at that time.
    """

    POTHOLE_ROAD_DAMAGE = "pothole_road_damage"
    STREETLIGHT_ELECTRICITY = "streetlight_electricity"
    WATER_LEAKAGE = "water_leakage"
    SEWAGE_DRAINAGE = "sewage_drainage"
    GARBAGE_WASTE = "garbage_waste"
    PUBLIC_INFRASTRUCTURE = "public_infrastructure"
    TRAFFIC_SIGNAGE = "traffic_signage"
    OTHER = "other"


# --- Evidence ---

class EvidenceProcessingStatus(str, Enum):
    """Processing status for uploaded evidence."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# --- AI Analysis ---

class AIAnalysisStatus(str, Enum):
    """Status of an AI analysis run."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# --- Assignment ---

class AssignmentStatus(str, Enum):
    """Status of a complaint assignment."""

    ACTIVE = "active"
    REASSIGNED = "reassigned"
    COMPLETED = "completed"


# --- Notification ---

class NotificationType(str, Enum):
    """Types of notifications sent to users."""

    STATUS_UPDATE = "status_update"
    ASSIGNMENT = "assignment"
    SYSTEM = "system"


class NotificationStatus(str, Enum):
    """Read/delivery state of a notification."""

    UNREAD = "unread"
    READ = "read"


# --- Prediction ---

class PredictionStatus(str, Enum):
    """Status of a prediction result."""

    ACTIVE = "active"
    EXPIRED = "expired"
    SUPERSEDED = "superseded"


class PredictionType(str, Enum):
    """Types of predictive analysis."""

    HOTSPOT = "hotspot"
    TREND = "trend"
    RECURRENCE = "recurrence"
