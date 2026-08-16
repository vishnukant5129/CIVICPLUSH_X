"""
CivicPulse AI — Routing Engine.
"""

import logging
from typing import Optional, Dict, Any, List
from pymongo.asynchronous.database import AsyncDatabase

from app.domain.authority_schemas import RoutingRule, RoutingResult
from app.domain.enums import ComplaintStatus
from app.domain.notification_schemas import EventType
from app.services.event_service import EventService
from app.services.notification_service import NotificationService

logger = logging.getLogger("civicpulse.routing")

class RoutingService:
    def __init__(self, db: AsyncDatabase):
        self.db = db
        
    async def route_complaint(self, complaint_id: str, category: str, jurisdiction_id: Optional[str]) -> RoutingResult:
        """
        Determines the appropriate department for a complaint based on data-driven RoutingRules.
        """
        logger.info(f"Routing complaint {complaint_id} (Category: {category}, Jurisdiction: {jurisdiction_id})")
        
        # 1. Fetch exact match for Category + Jurisdiction
        query = {"category": category, "active": True}
        if jurisdiction_id:
            query["jurisdiction"] = jurisdiction_id
            
        # Sort by priority ascending (1 is highest priority)
        rules_cursor = self.db["routing_rules"].find(query).sort("priority", 1)
        rules = await rules_cursor.to_list(length=None)
        
        # Fallback to Global Category rule if Jurisdiction-specific rule fails
        if not rules and jurisdiction_id:
            logger.info("Jurisdiction-specific rule not found. Attempting global fallback.")
            fallback_query = {"category": category, "active": True, "jurisdiction": None}
            fallback_cursor = self.db["routing_rules"].find(fallback_query).sort("priority", 1)
            rules = await fallback_cursor.to_list(length=None)
            
        if not rules:
            return RoutingResult(
                status="unavailable",
                explanation="No active routing rules found for this category and jurisdiction."
            )
            
        # Check for ambiguity
        top_priority = rules[0]["priority"]
        top_rules = [r for r in rules if r["priority"] == top_priority]
        
        if len(top_rules) > 1:
            return RoutingResult(
                status="ambiguous",
                explanation="Multiple active routing rules found with the same priority. Manual routing required."
            )
            
        best_rule = top_rules[0]
        
        # Update Complaint Assignment State
        assignment = {
            "complaint_id": complaint_id,
            "department_id": best_rule["department_id"],
            "assigned_authority_id": None,
            "created_at": best_rule.get("created_at", None), # Use DB generation
            "updated_at": None
        }
        
        # Idempotent assignment
        existing = await self.db["assignments"].find_one({"complaint_id": complaint_id})
        if not existing:
            await self.db["assignments"].insert_one(assignment)
        else:
            await self.db["assignments"].update_one(
                {"_id": existing["_id"]},
                {"$set": {"department_id": best_rule["department_id"]}}
            )
            
        # Trigger Domain Event & Notifications
        try:
            event_service = EventService(self.db)
            notification_service = NotificationService(self.db)
            event = await event_service.record_event(
                event_type=EventType.COMPLAINT_ROUTED,
                complaint_id=complaint_id,
                metadata={"department_id": best_rule["department_id"]},
            )
            if event:
                await notification_service.handle_domain_event(event)
        except Exception as e:
            logger.error(f"Error firing event/notification for routing complaint {complaint_id}: {e}")

        return RoutingResult(
            status="success",
            department_id=best_rule["department_id"],
            explanation=f"Routed to department {best_rule['department_id']} via rule priority {top_priority}."
        )
