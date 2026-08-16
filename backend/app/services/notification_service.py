"""
CivicPulse AI — Notification Service.

Handles event-to-notification mapping, template rendering, inbox retrieval,
read-state management, user preferences, and delivery dispatch.
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pymongo.asynchronous.database import AsyncDatabase

from app.domain.notification_schemas import (
    DeliveryChannel,
    DomainEvent,
    EventType,
    NotificationDocument,
    NotificationPreferences,
    NotificationResponse,
    NotificationType,
)
from app.services.notification_delivery_adapter import NotificationDeliveryAdapter

logger = logging.getLogger("civicpulse.notifications")


class NotificationService:
    """Service managing notification creation, inbox queries, and user preferences."""

    def __init__(self, db: AsyncDatabase):
        self.db = db
        self.delivery_adapter = NotificationDeliveryAdapter(db)

    # ----------------------------------------------------------------------
    # Preferences Management
    # ----------------------------------------------------------------------

    async def get_user_preferences(self, user_id: str) -> NotificationPreferences:
        """Get or initialize default notification preferences for a user."""
        doc = await self.db["user_notification_preferences"].find_one({"user_id": user_id})
        if doc:
            return NotificationPreferences(**doc)

        # Default preferences: In-app enabled, external disabled
        default_prefs = NotificationPreferences(user_id=user_id)
        return default_prefs

    async def update_user_preferences(
        self, user_id: str, preferences_update: Dict[str, Any]
    ) -> NotificationPreferences:
        """Update notification preferences for a user."""
        allowed_fields = {"in_app_enabled", "email_enabled", "sms_enabled", "push_enabled"}
        update_data = {k: v for k, v in preferences_update.items() if k in allowed_fields}
        update_data["updated_at"] = datetime.utcnow()

        await self.db["user_notification_preferences"].update_one(
            {"user_id": user_id},
            {"$set": update_data},
            upsert=True,
        )

        return await self.get_user_preferences(user_id)

    # ----------------------------------------------------------------------
    # Event-Driven Notification Handling
    # ----------------------------------------------------------------------

    async def handle_domain_event(self, event: DomainEvent) -> List[NotificationDocument]:
        """
        Process a domain event and dispatch notifications to relevant recipients.
        Safe: Never raises exceptions to caller.
        """
        created_notifications: List[NotificationDocument] = []
        try:
            # 1. Resolve complaint context if present
            complaint = None
            if event.complaint_id:
                complaint = await self.db["complaints"].find_one({"_id": event.complaint_id})

            # 2. Determine recipients and notification details
            recipients_data = await self._resolve_recipients_and_content(event, complaint)

            for recipient_id, notif_type, title, body, metadata in recipients_data:
                # Check user preferences
                prefs = await self.get_user_preferences(recipient_id)

                # Deterministic Notification ID for idempotency
                notif_id = f"notif_{event.event_id}_{recipient_id}"

                existing = await self.db["notifications"].find_one(
                    {"$or": [{"notification_id": notif_id}, {"_id": notif_id}]}
                )

                if existing:
                    notif = NotificationDocument(**existing)
                else:
                    notif = NotificationDocument(
                        notification_id=notif_id,
                        user_id=recipient_id,
                        event_id=event.event_id,
                        complaint_id=event.complaint_id,
                        type=notif_type,
                        title=title,
                        body=body,
                        created_at=datetime.utcnow(),
                        metadata=metadata,
                    )
                    doc = notif.model_dump(by_alias=True, exclude={"id"})
                    doc["recipient_id"] = recipient_id  # for schema compatibility
                    await self.db["notifications"].insert_one(doc)

                created_notifications.append(notif)

                # Dispatch to channels based on preferences
                if prefs.in_app_enabled:
                    await self.delivery_adapter.deliver(notif, DeliveryChannel.IN_APP)
                if prefs.email_enabled:
                    await self.delivery_adapter.deliver(notif, DeliveryChannel.EMAIL)
                if prefs.sms_enabled:
                    await self.delivery_adapter.deliver(notif, DeliveryChannel.SMS)
                if prefs.push_enabled:
                    await self.delivery_adapter.deliver(notif, DeliveryChannel.PUSH)

        except Exception as e:
            logger.error(f"Error handling domain event {event.event_id}: {e}", exc_info=True)

        return created_notifications

    async def _resolve_recipients_and_content(
        self, event: DomainEvent, complaint: Optional[Dict[str, Any]]
    ) -> List[tuple[str, NotificationType, str, str, Dict[str, Any]]]:
        """
        Generate (recipient_id, type, title, body, metadata) tuples based on event type.
        """
        results = []
        if not complaint and event.complaint_id:
            return results

        complaint_title = complaint.get("title", "Civic Complaint") if complaint else "Complaint"
        citizen_user_id = complaint.get("user_id") if complaint else None

        if event.event_type == EventType.COMPLAINT_CREATED and citizen_user_id:
            results.append((
                citizen_user_id,
                NotificationType.COMPLAINT_SUBMITTED,
                "Complaint Submitted",
                f"Your complaint '{complaint_title}' has been successfully logged.",
                {"complaint_id": event.complaint_id},
            ))

        elif event.event_type == EventType.COMPLAINT_ROUTED and citizen_user_id:
            dept_id = event.metadata.get("department_id", "assigned department")
            results.append((
                citizen_user_id,
                NotificationType.COMPLAINT_ROUTED,
                "Complaint Routed",
                f"Your complaint '{complaint_title}' has been routed to department '{dept_id}'.",
                {"complaint_id": event.complaint_id, "department_id": dept_id},
            ))

        elif event.event_type == EventType.COMPLAINT_ASSIGNED:
            if citizen_user_id:
                results.append((
                    citizen_user_id,
                    NotificationType.COMPLAINT_ASSIGNED,
                    "Complaint Assigned",
                    f"Your complaint '{complaint_title}' has been assigned to an official for resolution.",
                    {"complaint_id": event.complaint_id},
                ))
            # Also notify assigned authority if authority_id present
            assigned_authority_id = event.metadata.get("authority_id")
            if assigned_authority_id:
                results.append((
                    assigned_authority_id,
                    NotificationType.COMPLAINT_ASSIGNED,
                    "New Complaint Assignment",
                    f"You have been assigned to handle complaint '{complaint_title}'.",
                    {"complaint_id": event.complaint_id},
                ))

        elif event.event_type in (EventType.COMPLAINT_STATUS_CHANGED, EventType.COMPLAINT_RESOLVED, EventType.COMPLAINT_CLOSED):
            if citizen_user_id:
                new_st = (event.new_state or "updated").replace("_", " ").upper()
                results.append((
                    citizen_user_id,
                    NotificationType.STATUS_UPDATE,
                    f"Complaint Status: {new_st}",
                    f"Status of '{complaint_title}' changed to {new_st}.",
                    {"complaint_id": event.complaint_id, "status": event.new_state},
                ))

        elif event.event_type == EventType.AI_ANALYSIS_COMPLETED and citizen_user_id:
            category = event.metadata.get("category", "civil issue").replace("_", " ").title()
            results.append((
                citizen_user_id,
                NotificationType.AI_ANALYSIS_COMPLETED,
                "AI Evidence Processing Complete",
                f"AI analysis completed for '{complaint_title}' (Category: {category}).",
                {"complaint_id": event.complaint_id},
            ))

        return results

    # ----------------------------------------------------------------------
    # Inbox & Read State Operations
    # ----------------------------------------------------------------------

    async def get_user_notifications(
        self, user_id: str, unread_only: bool = False, skip: int = 0, limit: int = 20
    ) -> List[NotificationResponse]:
        """Fetch notifications for authenticated user."""
        query: Dict[str, Any] = {"$or": [{"user_id": user_id}, {"recipient_id": user_id}]}
        if unread_only:
            query["read_at"] = None

        cursor = (
            self.db["notifications"]
            .find(query)
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )

        docs = await cursor.to_list(length=limit)
        responses = []
        for d in docs:
            read_at = d.get("read_at")
            responses.append(
                NotificationResponse(
                    id=str(d.get("notification_id") or d.get("_id")),
                    user_id=user_id,
                    event_id=d.get("event_id"),
                    complaint_id=d.get("complaint_id"),
                    type=NotificationType(d.get("type", NotificationType.SYSTEM.value)),
                    title=d.get("title", ""),
                    body=d.get("body", ""),
                    read=read_at is not None,
                    read_at=read_at,
                    created_at=d.get("created_at", datetime.utcnow()),
                    metadata=d.get("metadata", {}),
                )
            )
        return responses

    async def get_unread_count(self, user_id: str) -> int:
        """Count unread notifications for authenticated user."""
        query = {
            "$or": [{"user_id": user_id}, {"recipient_id": user_id}],
            "read_at": None,
        }
        return await self.db["notifications"].count_documents(query)

    async def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        """Mark a single notification as read, enforcing user ownership."""
        query = {
            "$and": [
                {"$or": [{"notification_id": notification_id}, {"_id": notification_id}]},
                {"$or": [{"user_id": user_id}, {"recipient_id": user_id}]},
            ]
        }

        result = await self.db["notifications"].update_one(
            query,
            {"$set": {"read_at": datetime.utcnow()}},
        )
        return result.modified_count > 0 or result.matched_count > 0

    async def mark_all_as_read(self, user_id: str) -> int:
        """Mark all notifications for authenticated user as read."""
        query = {
            "$or": [{"user_id": user_id}, {"recipient_id": user_id}],
            "read_at": None,
        }
        result = await self.db["notifications"].update_many(
            query,
            {"$set": {"read_at": datetime.utcnow()}},
        )
        return result.modified_count
