"""
CivicPulse AI — Complaint Service.

Coordinates domain logic for complaints, including persistence
sequencing and ownership enforcement.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pymongo.asynchronous.database import AsyncDatabase

from app.domain.complaint_schemas import ComplaintCreateRequest
from app.domain.enums import ComplaintStatus
from app.domain.notification_schemas import EventType
from app.repositories.collections import ComplaintRepository, StatusHistoryRepository
from app.services.event_service import EventService
from app.services.notification_service import NotificationService

logger = logging.getLogger("civicpulse.complaints")


class ComplaintService:
    """Coordinates complaint business logic."""

    def __init__(self, db: AsyncDatabase):
        self.db = db
        self.complaint_repo = ComplaintRepository(db)
        self.status_history_repo = StatusHistoryRepository(db)

    async def create_complaint(
        self, user_id: str, request: ComplaintCreateRequest
    ) -> Dict[str, Any]:
        """
        Create a new complaint and its initial status history.
        """
        # 1. Prepare Complaint Document
        now = datetime.now(timezone.utc)
        complaint_doc = {
            "user_id": user_id,
            "title": request.title,
            "description": request.description,
            "category": request.category.value,
            "location": request.location.model_dump(),
            "status": ComplaintStatus.SUBMITTED.value,
            "evidence_count": 0,
            "created_at": now,
            "updated_at": now,
        }

        # Note: We rely on the repository to add created_at/updated_at and validate.
        # While MongoDB supports transactions, standard replica sets are required.
        # For this MVP phase, we use sequential inserts.
        
        complaint_id = await self.complaint_repo.insert_one(complaint_doc)
        
        # 2. Prepare Status History Document
        history_doc = {
            "complaint_id": complaint_id,
            "previous_status": None,
            "new_status": ComplaintStatus.SUBMITTED.value,
            "actor_id": user_id,
            "reason": "Initial submission.",
            "created_at": now,
        }
        
        try:
            await self.status_history_repo.insert_one(history_doc)
        except Exception as e:
            # If history fails, we still have the complaint. Log it.
            logger.error(f"Failed to insert status history for complaint {complaint_id}: {e}")

        logger.info(f"Complaint {complaint_id} created by user {user_id}")
        
        # Trigger Domain Event & Notifications
        try:
            event_service = EventService(self.db)
            notification_service = NotificationService(self.db)
            event = await event_service.record_event(
                event_type=EventType.COMPLAINT_CREATED,
                complaint_id=complaint_id,
                actor_id=user_id,
                new_state=ComplaintStatus.SUBMITTED.value,
            )
            if event:
                await notification_service.handle_domain_event(event)
        except Exception as e:
            logger.error(f"Error firing event/notification for complaint {complaint_id}: {e}")

        # Return fully constructed document
        created_complaint = await self.complaint_repo.find_by_id(complaint_id)
        if not created_complaint:
            raise RuntimeError("Failed to retrieve created complaint.")
        return created_complaint

    async def get_user_complaints(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all complaints owned by the user."""
        return await self.complaint_repo.find_by_user(user_id)

    async def get_complaint_detail(self, complaint_id: str, requesting_user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get complaint details, enforcing ownership.
        Returns None if not found OR if user is not authorized to view it
        (to prevent existence leakage).
        """
        complaint = await self.complaint_repo.find_by_id(complaint_id)
        if not complaint:
            return None
            
        if complaint.get("user_id") != requesting_user_id:
            logger.warning(f"User {requesting_user_id} attempted to access complaint {complaint_id} owned by {complaint.get('user_id')}")
            return None
            
        return complaint

    async def get_complaint_status_history(self, complaint_id: str, requesting_user_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get complaint status history, enforcing ownership.
        """
        # First verify ownership
        complaint = await self.get_complaint_detail(complaint_id, requesting_user_id)
        if not complaint:
            return None
            
        return await self.status_history_repo.find_by_complaint(complaint_id)
