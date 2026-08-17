"""
CivicPulse AI — Collection-Specific Repositories.

Each repository extends BaseRepository with collection-specific
query methods required by the domain.

These repositories contain ONLY database query logic.
They do NOT contain: HTTP handling, authorization, AI/LLM logic.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from pymongo import ASCENDING, DESCENDING
from pymongo.asynchronous.database import AsyncDatabase

from app.database.init_db import (
    COLLECTION_AI_ANALYSES,
    COLLECTION_ASSIGNMENTS,
    COLLECTION_AUDIT_LOGS,
    COLLECTION_COMPLAINTS,
    COLLECTION_DEPARTMENTS,
    COLLECTION_EVIDENCE,
    COLLECTION_INCIDENT_CLUSTERS,
    COLLECTION_NOTIFICATIONS,
    COLLECTION_PREDICTIONS,
    COLLECTION_STATUS_HISTORY,
    COLLECTION_USERS,
    COLLECTION_WARDS,
    COLLECTION_ORGANIZATIONS,
    COLLECTION_CIVIC_PROJECTS,
    COLLECTION_MATCH_REQUESTS,
)
from app.repositories.base import BaseRepository


# ============================================================
# User Repository
# ============================================================

class UserRepository(BaseRepository):
    """Repository for user documents."""

    collection_name = COLLECTION_USERS

    async def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find a user by normalized email (case-insensitive lookup)."""
        return await self.find_one({"normalized_email": email.lower().strip()})

    async def find_by_google_sub(self, google_sub: str) -> Optional[Dict[str, Any]]:
        """Find a user by their stable Google subject identifier."""
        return await self.find_one({"google_sub": google_sub})


# ============================================================
# Department Repository
# ============================================================

class DepartmentRepository(BaseRepository):
    """Repository for department documents."""

    collection_name = COLLECTION_DEPARTMENTS

    async def find_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """Find a department by its unique code."""
        return await self.find_one({"code": code})

    async def find_active(self) -> List[Dict[str, Any]]:
        """Find all active departments."""
        return await self.find_many(
            {"status": "active"},
            sort=[("name", ASCENDING)],
            limit=200,
        )


# ============================================================
# Ward Repository
# ============================================================

class WardRepository(BaseRepository):
    """Repository for ward documents."""

    collection_name = COLLECTION_WARDS

    async def find_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """Find a ward by its unique code."""
        return await self.find_one({"code": code})

    async def find_active(self) -> List[Dict[str, Any]]:
        """Find all active wards."""
        return await self.find_many(
            {"status": "active"},
            sort=[("name", ASCENDING)],
            limit=200,
        )


# ============================================================
# Complaint Repository
# ============================================================

class ComplaintRepository(BaseRepository):
    """Repository for complaint documents."""

    collection_name = COLLECTION_COMPLAINTS

    async def find_by_user(
        self,
        user_id: str,
        *,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Find complaints submitted by a specific user."""
        return await self.find_many(
            {"user_id": user_id},
            sort=[("created_at", DESCENDING)],
            skip=skip,
            limit=limit,
        )

    async def find_by_status(
        self,
        status: str,
        *,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Find complaints with a specific status."""
        return await self.find_many(
            {"status": status},
            sort=[("priority_score", DESCENDING), ("created_at", DESCENDING)],
            skip=skip,
            limit=limit,
        )

    async def find_nearby(
        self,
        longitude: float,
        latitude: float,
        max_distance_meters: float = 1000,
        *,
        additional_filter: Optional[Dict[str, Any]] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Find complaints near a geographic point."""
        return await self.find_near(
            field="location.geo",
            longitude=longitude,
            latitude=latitude,
            max_distance_meters=max_distance_meters,
            filter=additional_filter,
            limit=limit,
        )

    async def find_by_cluster(self, cluster_id: str) -> List[Dict[str, Any]]:
        """Find all complaints belonging to a cluster."""
        return await self.find_many(
            {"cluster_id": cluster_id},
            sort=[("created_at", DESCENDING)],
            limit=200,
        )


# ============================================================
# Evidence Repository
# ============================================================

class EvidenceRepository(BaseRepository):
    """Repository for evidence documents."""

    collection_name = COLLECTION_EVIDENCE

    async def find_by_complaint(self, complaint_id: str) -> List[Dict[str, Any]]:
        """Find all evidence for a specific complaint."""
        return await self.find_many(
            {"complaint_id": complaint_id},
            sort=[("created_at", ASCENDING)],
            limit=50,
        )


# ============================================================
# AI Analysis Repository
# ============================================================

class AIAnalysisRepository(BaseRepository):
    """Repository for AI analysis documents."""

    collection_name = COLLECTION_AI_ANALYSES

    async def find_latest_for_complaint(
        self, complaint_id: str
    ) -> Optional[Dict[str, Any]]:
        """Find the most recent analysis for a complaint."""
        results = await self.find_many(
            {"complaint_id": complaint_id},
            sort=[("created_at", DESCENDING)],
            limit=1,
        )
        return results[0] if results else None

    async def find_by_complaint(self, complaint_id: str) -> List[Dict[str, Any]]:
        """Find all analyses for a specific complaint."""
        return await self.find_many(
            {"complaint_id": complaint_id},
            sort=[("created_at", DESCENDING)],
            limit=50,
        )


# ============================================================
# Incident Cluster Repository
# ============================================================

class IncidentClusterRepository(BaseRepository):
    """Repository for incident cluster documents."""

    collection_name = COLLECTION_INCIDENT_CLUSTERS

    async def find_by_category(
        self, category: str
    ) -> List[Dict[str, Any]]:
        """Find clusters of a specific category."""
        return await self.find_many(
            {"category": category},
            sort=[("complaint_count", DESCENDING)],
            limit=100,
        )


# ============================================================
# Assignment Repository
# ============================================================

class AssignmentRepository(BaseRepository):
    """Repository for assignment documents."""

    collection_name = COLLECTION_ASSIGNMENTS

    async def find_by_complaint(
        self, complaint_id: str
    ) -> List[Dict[str, Any]]:
        """Find all assignments for a complaint (including reassignments)."""
        return await self.find_many(
            {"complaint_id": complaint_id},
            sort=[("assigned_at", DESCENDING)],
            limit=50,
        )

    async def find_active_by_department(
        self,
        department_id: str,
        *,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Find active assignments for a department."""
        return await self.find_many(
            {"department_id": department_id, "status": "active"},
            sort=[("assigned_at", DESCENDING)],
            skip=skip,
            limit=limit,
        )


# ============================================================
# Status History Repository
# ============================================================

class StatusHistoryRepository(BaseRepository):
    """Repository for status history documents."""

    collection_name = COLLECTION_STATUS_HISTORY

    async def find_by_complaint(
        self, complaint_id: str
    ) -> List[Dict[str, Any]]:
        """Find status history for a complaint (chronological)."""
        return await self.find_many(
            {"complaint_id": complaint_id},
            sort=[("created_at", ASCENDING)],
            limit=200,
        )


# ============================================================
# Notification Repository
# ============================================================

class NotificationRepository(BaseRepository):
    """Repository for notification documents."""

    collection_name = COLLECTION_NOTIFICATIONS

    async def find_by_recipient(
        self,
        recipient_id: str,
        *,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Find notifications for a user (newest first)."""
        return await self.find_many(
            {"recipient_id": recipient_id},
            sort=[("created_at", DESCENDING)],
            skip=skip,
            limit=limit,
        )

    async def count_unread(self, recipient_id: str) -> int:
        """Count unread notifications for a user."""
        return await self.count(
            {"recipient_id": recipient_id, "status": "unread"}
        )


# ============================================================
# Prediction Repository
# ============================================================

class PredictionRepository(BaseRepository):
    """Repository for prediction documents."""

    collection_name = COLLECTION_PREDICTIONS

    async def find_latest_by_type(
        self,
        prediction_type: str,
    ) -> Optional[Dict[str, Any]]:
        """Find the most recently generated prediction for a specific prediction_type."""
        results = await self.find_many(
            {"prediction_type": prediction_type},
            sort=[("generated_at", DESCENDING)],
            limit=1,
        )
        return results[0] if results else None

    async def find_latest(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Find recent prediction documents."""
        return await self.find_many(
            {},
            sort=[("generated_at", DESCENDING)],
            limit=limit,
        )


# ============================================================
# Audit Log Repository
# ============================================================

class AuditLogRepository(BaseRepository):
    """Repository for audit log documents."""

    collection_name = COLLECTION_AUDIT_LOGS

    async def find_by_resource(
        self,
        resource_type: str,
        resource_id: str,
        *,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Find audit log entries for a specific resource."""
        return await self.find_many(
            {"resource_type": resource_type, "resource_id": resource_id},
            sort=[("created_at", DESCENDING)],
            limit=limit,
        )

    async def find_by_actor(
        self,
        actor_id: str,
        *,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Find audit log entries by actor."""
        return await self.find_many(
            {"actor_id": actor_id},
            sort=[("created_at", DESCENDING)],
            skip=skip,
            limit=limit,
        )

# ============================================================
# Organization Repository
# ============================================================

class OrganizationRepository(BaseRepository):
    collection_name = COLLECTION_ORGANIZATIONS

    async def find_verified(self, limit: int = 50) -> List[Dict[str, Any]]:
        return await self.find_many(
            {"verification_status": "verified"},
            sort=[("name", ASCENDING)],
            limit=limit,
        )


# ============================================================
# Civic Project Repository
# ============================================================

class CivicProjectRepository(BaseRepository):
    collection_name = COLLECTION_CIVIC_PROJECTS

    async def find_by_status(self, status: str, limit: int = 50) -> List[Dict[str, Any]]:
        return await self.find_many(
            {"status": status},
            sort=[("created_at", DESCENDING)],
            limit=limit,
        )


# ============================================================
# Resource Match Request Repository
# ============================================================

class ResourceMatchRequestRepository(BaseRepository):
    collection_name = COLLECTION_MATCH_REQUESTS

    async def find_by_project(self, project_id: str) -> List[Dict[str, Any]]:
        return await self.find_many(
            {"project_id": project_id},
            sort=[("created_at", DESCENDING)],
            limit=50,
        )

