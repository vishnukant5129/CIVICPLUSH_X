"""
CivicPulse AI — Domain Event Service.

Handles recording, idempotency checking, and dispatching of domain events.
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, Optional
from pymongo.asynchronous.database import AsyncDatabase

from app.domain.notification_schemas import DomainEvent, EventType

logger = logging.getLogger("civicpulse.events")


class EventService:
    """Domain Event recording and distribution service."""

    def __init__(self, db: AsyncDatabase):
        self.db = db

    async def record_event(
        self,
        event_type: EventType,
        complaint_id: Optional[str] = None,
        actor_id: Optional[str] = None,
        previous_state: Optional[str] = None,
        new_state: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        event_id: Optional[str] = None,
    ) -> Optional[DomainEvent]:
        """
        Record an immutable domain event.
        Idempotent: If event_id is supplied and already recorded, returns existing event.
        """
        if not event_id:
            # Deterministic/unique ID generation if not provided
            event_id = f"evt_{uuid.uuid4().hex[:16]}"

        existing = await self.db["domain_events"].find_one({"event_id": event_id})
        if existing:
            logger.info(f"Domain event {event_id} already exists (idempotent skip).")
            return DomainEvent(**existing)

        event = DomainEvent(
            event_id=event_id,
            event_type=event_type,
            complaint_id=complaint_id,
            actor_id=actor_id,
            previous_state=previous_state,
            new_state=new_state,
            metadata=metadata or {},
            created_at=datetime.utcnow(),
        )

        try:
            doc = event.model_dump(by_alias=True, exclude={"id"})
            await self.db["domain_events"].insert_one(doc)
            logger.info(f"Recorded domain event {event.event_id} ({event_type})")
            return event
        except Exception as e:
            logger.error(f"Failed to record domain event {event_id}: {e}")
            return None
