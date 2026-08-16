"""
CivicPulse AI — Government Integration Adapter Boundary.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
from pymongo.asynchronous.database import AsyncDatabase
from app.domain.authority_schemas import ExternalIntegrationDelivery, IntegrationStatus

logger = logging.getLogger("civicpulse.integration")

class GovernmentIntegrationAdapter:
    """
    Abstract boundary for government integrations.
    Because no real government integration API specification exists,
    this interface reliably returns an honest NOT_CONFIGURED state,
    preventing fabricated data flow.
    """
    
    def __init__(self, db: AsyncDatabase):
        self.db = db
        # If a real API was provided, credentials would be loaded here.
        self.is_configured = False
        self.provider_name = "unavailable_external_provider"
        
    async def deliver_complaint(self, complaint_id: str, complaint_data: Dict[str, Any]) -> ExternalIntegrationDelivery:
        """
        Attempt to deliver a complaint to an external municipal system.
        """
        logger.info(f"Integration delivery requested for complaint {complaint_id}")
        
        # Idempotency check: Don't deliver if already sent or acknowledged.
        existing = await self.db["integration_deliveries"].find_one({
            "complaint_id": complaint_id,
            "status": {"$in": [IntegrationStatus.SENT.value, IntegrationStatus.ACKNOWLEDGED.value]}
        })
        if existing:
            return ExternalIntegrationDelivery(**existing)
            
        delivery = ExternalIntegrationDelivery(
            complaint_id=complaint_id,
            integration_id="mock-integration",
            provider=self.provider_name,
            status=IntegrationStatus.NOT_CONFIGURED,
            error_reason="No external government API integration is configured.",
            request_timestamp=datetime.utcnow()
        )
        
        if not self.is_configured:
            # We explicitly decline to fabricate a successful connection.
            await self.db["integration_deliveries"].insert_one(delivery.model_dump(exclude={"id"}))
            return delivery
            
        # If a real API is configured, the logic would execute HTTP calls here.
        # Ensure requests use appropriate timeouts and handle 4xx/5xx natively.
        
        return delivery
