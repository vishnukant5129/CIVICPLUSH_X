"""
CivicPulse AI — Database Initialization & Index Management.

Provides idempotent index creation for all CivicPulse collections.
Safe to run multiple times — uses create_index which is a no-op for
existing indexes with the same specification.

This module is called during application startup after MongoDB
connection is established.

SECURITY:
- No production data is created.
- No fake records are inserted.
- Only indexes and collection validation are established.
"""

from __future__ import annotations

import logging
from typing import Optional

from pymongo import ASCENDING, DESCENDING, GEOSPHERE
from pymongo.asynchronous.database import AsyncDatabase

logger = logging.getLogger("civicpulse.database.init")

# ============================================================
# Collection names — single source of truth
# ============================================================

COLLECTION_USERS = "users"
COLLECTION_DEPARTMENTS = "departments"
COLLECTION_COMPLAINTS = "complaints"
COLLECTION_EVIDENCE = "evidence"
COLLECTION_AI_ANALYSES = "ai_analyses"
COLLECTION_INCIDENT_CLUSTERS = "incident_clusters"
COLLECTION_ASSIGNMENTS = "assignments"
COLLECTION_STATUS_HISTORY = "status_history"
COLLECTION_NOTIFICATIONS = "notifications"
COLLECTION_PREDICTIONS = "predictions"
COLLECTION_AUDIT_LOGS = "audit_logs"


async def ensure_indexes(db: AsyncDatabase) -> None:
    """
    Create all required indexes idempotently.

    Each create_index call is a no-op if the index already exists
    with the same specification. Safe to call on every startup.

    Args:
        db: The AsyncDatabase instance to create indexes on.
    """
    logger.info("Ensuring database indexes...")

    await _ensure_user_indexes(db)
    await _ensure_department_indexes(db)
    await _ensure_complaint_indexes(db)
    await _ensure_evidence_indexes(db)
    await _ensure_ai_analysis_indexes(db)
    await _ensure_incident_cluster_indexes(db)
    await _ensure_assignment_indexes(db)
    await _ensure_status_history_indexes(db)
    await _ensure_notification_indexes(db)
    await _ensure_prediction_indexes(db)
    await _ensure_audit_log_indexes(db)

    logger.info("Database indexes ensured successfully.")


# ============================================================
# Per-collection index definitions
# ============================================================

async def _ensure_user_indexes(db: AsyncDatabase) -> None:
    """
    Users indexes.

    - normalized_email: unique — enforces email uniqueness at DB level.
      Case-insensitive uniqueness achieved by indexing the normalized
      (lowercased) email field.
    - role: non-unique — supports filtering users by role.
    - status: non-unique — supports filtering active/inactive users.
    """
    coll = db[COLLECTION_USERS]
    await coll.create_index(
        [(("normalized_email", ASCENDING))],
        unique=True,
        name="idx_users_normalized_email_unique",
    )
    await coll.create_index(
        [("google_sub", ASCENDING)],
        unique=True,
        sparse=True,  # Only indexes documents where google_sub is present
        name="idx_users_google_sub_unique",
    )
    await coll.create_index(
        [("role", ASCENDING)],
        name="idx_users_role",
    )
    await coll.create_index(
        [("status", ASCENDING)],
        name="idx_users_status",
    )


async def _ensure_department_indexes(db: AsyncDatabase) -> None:
    """
    Departments indexes.

    - code: unique — department codes must be unique for routing.
    - status: non-unique — supports filtering active departments.
    """
    coll = db[COLLECTION_DEPARTMENTS]
    await coll.create_index(
        [("code", ASCENDING)],
        unique=True,
        name="idx_departments_code_unique",
    )
    await coll.create_index(
        [("status", ASCENDING)],
        name="idx_departments_status",
    )


async def _ensure_complaint_indexes(db: AsyncDatabase) -> None:
    """
    Complaints indexes.

    - user_id: supports "my complaints" queries.
    - status: supports filtering by lifecycle status.
    - category: supports filtering by civic category.
    - created_at DESC: supports chronological listing.
    - location.geo: 2dsphere — supports geospatial queries ($near, $geoWithin).
    - status + priority_score DESC + created_at DESC: compound — supports
      authority dashboard queue (filter by status, sort by priority then recency).
    - cluster_id: supports cluster membership queries.
    - department_id: supports department-specific queries.
    """
    coll = db[COLLECTION_COMPLAINTS]

    await coll.create_index(
        [("user_id", ASCENDING)],
        name="idx_complaints_user_id",
    )
    await coll.create_index(
        [("status", ASCENDING)],
        name="idx_complaints_status",
    )
    await coll.create_index(
        [("category", ASCENDING)],
        name="idx_complaints_category",
    )
    await coll.create_index(
        [("created_at", DESCENDING)],
        name="idx_complaints_created_at_desc",
    )
    # Geospatial index for location queries
    await coll.create_index(
        [("location.geo", GEOSPHERE)],
        name="idx_complaints_location_geo_2dsphere",
    )
    # Compound index for authority dashboard queue
    await coll.create_index(
        [
            ("status", ASCENDING),
            ("priority_score", DESCENDING),
            ("created_at", DESCENDING),
        ],
        name="idx_complaints_status_priority_created",
    )
    await coll.create_index(
        [("cluster_id", ASCENDING)],
        name="idx_complaints_cluster_id",
    )
    await coll.create_index(
        [("department_id", ASCENDING)],
        name="idx_complaints_department_id",
    )


async def _ensure_evidence_indexes(db: AsyncDatabase) -> None:
    """
    Evidence indexes.

    - complaint_id: supports fetching evidence for a complaint.
    """
    coll = db[COLLECTION_EVIDENCE]
    await coll.create_index(
        [("complaint_id", ASCENDING)],
        name="idx_evidence_complaint_id",
    )


async def _ensure_ai_analysis_indexes(db: AsyncDatabase) -> None:
    """
    AI Analyses indexes.

    - complaint_id: supports fetching analyses for a complaint.
    - complaint_id + created_at DESC: supports getting latest analysis.
    """
    coll = db[COLLECTION_AI_ANALYSES]
    await coll.create_index(
        [("complaint_id", ASCENDING)],
        name="idx_ai_analyses_complaint_id",
    )
    await coll.create_index(
        [("complaint_id", ASCENDING), ("created_at", DESCENDING)],
        name="idx_ai_analyses_complaint_created_desc",
    )


async def _ensure_incident_cluster_indexes(db: AsyncDatabase) -> None:
    """
    Incident Clusters indexes.

    - category: supports filtering clusters by type.
    - representative_location: 2dsphere — supports geospatial cluster queries.
    """
    coll = db[COLLECTION_INCIDENT_CLUSTERS]
    await coll.create_index(
        [("category", ASCENDING)],
        name="idx_incident_clusters_category",
    )
    # Geospatial on representative location (sparse — only when set)
    await coll.create_index(
        [("representative_location", GEOSPHERE)],
        name="idx_incident_clusters_location_2dsphere",
        sparse=True,
    )


async def _ensure_assignment_indexes(db: AsyncDatabase) -> None:
    """
    Assignments indexes.

    - complaint_id: supports fetching assignments for a complaint.
    - department_id: supports department workload queries.
    """
    coll = db[COLLECTION_ASSIGNMENTS]
    await coll.create_index(
        [("complaint_id", ASCENDING)],
        name="idx_assignments_complaint_id",
    )
    await coll.create_index(
        [("department_id", ASCENDING)],
        name="idx_assignments_department_id",
    )


async def _ensure_status_history_indexes(db: AsyncDatabase) -> None:
    """
    Status History indexes.

    - complaint_id + created_at ASC: supports chronological timeline
      for a complaint's status history.
    """
    coll = db[COLLECTION_STATUS_HISTORY]
    await coll.create_index(
        [("complaint_id", ASCENDING), ("created_at", ASCENDING)],
        name="idx_status_history_complaint_created",
    )


async def _ensure_notification_indexes(db: AsyncDatabase) -> None:
    """
    Notifications indexes.

    - recipient_id + created_at DESC: supports user notification feed.
    - recipient_id + status: supports unread count queries.
    """
    coll = db[COLLECTION_NOTIFICATIONS]
    await coll.create_index(
        [("recipient_id", ASCENDING), ("created_at", DESCENDING)],
        name="idx_notifications_recipient_created_desc",
    )
    await coll.create_index(
        [("recipient_id", ASCENDING), ("status", ASCENDING)],
        name="idx_notifications_recipient_status",
    )


async def _ensure_prediction_indexes(db: AsyncDatabase) -> None:
    """
    Predictions indexes.

    - prediction_type + status: supports active prediction queries.
    - generated_at DESC: supports chronological listing.
    """
    coll = db[COLLECTION_PREDICTIONS]
    await coll.create_index(
        [("prediction_type", ASCENDING), ("status", ASCENDING)],
        name="idx_predictions_type_status",
    )
    await coll.create_index(
        [("generated_at", DESCENDING)],
        name="idx_predictions_generated_at_desc",
    )


async def _ensure_audit_log_indexes(db: AsyncDatabase) -> None:
    """
    Audit Logs indexes.

    - resource_type + resource_id: supports resource-specific audit trail.
    - created_at DESC: supports chronological audit queries.
    - actor_id: supports actor-specific audit queries.
    """
    coll = db[COLLECTION_AUDIT_LOGS]
    await coll.create_index(
        [("resource_type", ASCENDING), ("resource_id", ASCENDING)],
        name="idx_audit_logs_resource",
    )
    await coll.create_index(
        [("created_at", DESCENDING)],
        name="idx_audit_logs_created_at_desc",
    )
    await coll.create_index(
        [("actor_id", ASCENDING)],
        name="idx_audit_logs_actor_id",
    )
