"""
CivicPulse AI — External Delivery Adapter Boundary.

Provides channel delivery implementations for In-App, Email, SMS, and Push notifications.
Enforces strict honesty: if no external provider is configured, sets status to NOT_CONFIGURED.
"""

import logging
from datetime import datetime
from typing import Optional
from pymongo.asynchronous.database import AsyncDatabase

from app.config import get_settings
from app.domain.notification_schemas import (
    DeliveryChannel,
    DeliveryRecord,
    DeliveryStatus,
    NotificationDocument,
)

logger = logging.getLogger("civicpulse.delivery")


class NotificationDeliveryAdapter:
    """Boundary provider for external and internal notification channels."""

    def __init__(self, db: AsyncDatabase):
        self.db = db
        self.settings = get_settings()

    async def deliver(
        self, notification: NotificationDocument, channel: DeliveryChannel
    ) -> DeliveryRecord:
        """Deliver notification to specified channel and persist audit record."""
        # Idempotency check: return existing delivery record if channel already processed
        existing = await self.db["notification_deliveries"].find_one(
            {
                "notification_id": notification.notification_id,
                "channel": channel.value,
            }
        )
        if existing:
            return DeliveryRecord(**existing)

        if channel == DeliveryChannel.IN_APP:
            record = DeliveryRecord(
                notification_id=notification.notification_id,
                channel=DeliveryChannel.IN_APP,
                provider="internal_mongodb",
                status=DeliveryStatus.PERSISTED,
                attempted_at=datetime.utcnow(),
            )
        else:
            # Check if external provider is configured in environment
            # In MVP, external providers (SMTP, Twilio, FCM) are not configured by default
            is_configured = False
            provider_name = f"unconfigured_{channel.value}_provider"

            record = DeliveryRecord(
                notification_id=notification.notification_id,
                channel=channel,
                provider=provider_name,
                status=DeliveryStatus.NOT_CONFIGURED if not is_configured else DeliveryStatus.SENT,
                attempted_at=datetime.utcnow(),
                error_reason=f"External {channel.value} delivery provider is not configured in backend settings.",
            )

        try:
            doc = record.model_dump(by_alias=True, exclude={"id"})
            await self.db["notification_deliveries"].insert_one(doc)
        except Exception as e:
            logger.error(f"Failed to persist delivery record for {notification.notification_id}: {e}")

        return record
