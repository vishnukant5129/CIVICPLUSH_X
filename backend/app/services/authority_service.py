"""
CivicPulse AI — Authority Operations Service.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from pymongo.asynchronous.database import AsyncDatabase

from app.domain.authority_schemas import AuthorityActionHistory, AuthorityActionType
from app.domain.enums import ComplaintStatus
from app.domain.notification_schemas import EventType
from app.services.event_service import EventService
from app.services.notification_service import NotificationService

logger = logging.getLogger("civicpulse.authority")

class AuthorityService:
    def __init__(self, db: AsyncDatabase):
        self.db = db
        
    async def log_audit(self, action: AuthorityActionHistory) -> None:
        """Append-only immutable audit trail recording."""
        await self.db["authority_audit_trail"].insert_one(action.model_dump(exclude={"id"}))

    async def _validate_transition(self, current: ComplaintStatus, target: ComplaintStatus) -> bool:
        """
        Validate complaint lifecycle transitions.
        Rule: SUBMITTED -> ASSIGNED -> IN_PROGRESS -> RESOLVED -> CLOSED
        """
        valid_transitions = {
            ComplaintStatus.SUBMITTED: [ComplaintStatus.ASSIGNED, ComplaintStatus.REJECTED, ComplaintStatus.INVALID],
            ComplaintStatus.ASSIGNED: [ComplaintStatus.IN_PROGRESS, ComplaintStatus.REJECTED],
            ComplaintStatus.IN_PROGRESS: [ComplaintStatus.RESOLVED],
            ComplaintStatus.RESOLVED: [ComplaintStatus.CLOSED, ComplaintStatus.IN_PROGRESS], # Reopen allowed
            ComplaintStatus.CLOSED: [],
            ComplaintStatus.REJECTED: [],
            ComplaintStatus.DUPLICATE: [],
            ComplaintStatus.INVALID: []
        }
        return target in valid_transitions.get(current, [])
        
    async def assign_complaint(self, complaint_id: str, authority_id: str, department_id: str, actor_id: str) -> bool:
        """Assign an authority to a complaint."""
        complaint = await self.db["complaints"].find_one({"_id": complaint_id})
        if not complaint:
            return False
            
        current_status = ComplaintStatus(complaint["status"])
        
        # We allow assignment if it's currently submitted or already assigned to someone else
        if current_status not in [ComplaintStatus.SUBMITTED, ComplaintStatus.ASSIGNED, ComplaintStatus.IN_PROGRESS]:
            raise ValueError(f"Cannot assign complaint in state {current_status}")

        existing = await self.db["assignments"].find_one({"complaint_id": complaint_id})
        
        if not existing:
            await self.db["assignments"].insert_one({
                "complaint_id": complaint_id,
                "department_id": department_id,
                "assigned_authority_id": authority_id,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
        else:
            await self.db["assignments"].update_one(
                {"_id": existing["_id"]},
                {"$set": {
                    "department_id": department_id,
                    "assigned_authority_id": authority_id,
                    "updated_at": datetime.utcnow()
                }}
            )
            
        # Update Complaint Status to ASSIGNED if it was SUBMITTED
        if current_status == ComplaintStatus.SUBMITTED:
            await self.db["complaints"].update_one(
                {"_id": complaint_id},
                {"$set": {"status": ComplaintStatus.ASSIGNED.value}}
            )
            # Log Status Audit
            await self.log_audit(AuthorityActionHistory(
                complaint_id=complaint_id,
                actor_id=actor_id,
                action_type=AuthorityActionType.STATUS_UPDATE,
                previous_status=ComplaintStatus.SUBMITTED,
                new_status=ComplaintStatus.ASSIGNED,
                note="Automatically updated to ASSIGNED upon authority assignment."
            ))

        # Log Assignment Audit
        await self.log_audit(AuthorityActionHistory(
            complaint_id=complaint_id,
            actor_id=actor_id,
            action_type=AuthorityActionType.ASSIGNED,
            note=f"Assigned to Authority ID: {authority_id} in Dept: {department_id}"
        ))

        # Fire Domain Event & Notifications
        try:
            event_service = EventService(self.db)
            notification_service = NotificationService(self.db)
            event = await event_service.record_event(
                event_type=EventType.COMPLAINT_ASSIGNED,
                complaint_id=complaint_id,
                actor_id=actor_id,
                new_state=ComplaintStatus.ASSIGNED.value,
                metadata={"department_id": department_id, "authority_id": authority_id},
            )
            if event:
                await notification_service.handle_domain_event(event)
        except Exception as e:
            logger.error(f"Error firing event/notification for assignment {complaint_id}: {e}")

        return True

    async def update_status(self, complaint_id: str, actor_id: str, new_status: ComplaintStatus, note: Optional[str] = None) -> bool:
        """Update complaint status and record audit log."""
        complaint = await self.db["complaints"].find_one({"_id": complaint_id})
        if not complaint:
            return False
            
        current_status = ComplaintStatus(complaint["status"])
        if current_status == new_status:
            return True # Idempotent
            
        if not await self._validate_transition(current_status, new_status):
            raise ValueError(f"Invalid state transition from {current_status} to {new_status}")
            
        await self.db["complaints"].update_one(
            {"_id": complaint_id},
            {"$set": {"status": new_status.value}}
        )
        
        await self.log_audit(AuthorityActionHistory(
            complaint_id=complaint_id,
            actor_id=actor_id,
            action_type=AuthorityActionType.STATUS_UPDATE,
            previous_status=current_status,
            new_status=new_status,
            note=note
        ))

        # Fire Domain Event & Notifications
        try:
            event_service = EventService(self.db)
            notification_service = NotificationService(self.db)
            evt_type = EventType.COMPLAINT_RESOLVED if new_status == ComplaintStatus.RESOLVED else (
                EventType.COMPLAINT_CLOSED if new_status == ComplaintStatus.CLOSED else EventType.COMPLAINT_STATUS_CHANGED
            )
            event = await event_service.record_event(
                event_type=evt_type,
                complaint_id=complaint_id,
                actor_id=actor_id,
                previous_state=current_status.value,
                new_state=new_status.value,
                metadata={"note": note} if note else {},
            )
            if event:
                await notification_service.handle_domain_event(event)
        except Exception as e:
            logger.error(f"Error firing event/notification for status update {complaint_id}: {e}")
        
        return True

    async def get_authority_dashboard_summary(
        self, user_id: str, role: str, department_id: Optional[str] = None, ward_ids: List[str] = None
    ) -> Dict[str, Any]:
        """
        Aggregate operational dashboard statistics for authority & admin users.
        """
        match_filter: Dict[str, Any] = {}
        scope_note = "Global system view (Admin)"

        if role == "authority":
            if department_id:
                dept_or = [{"department_id": department_id}, {"assigned_authority_id": user_id}]
                if ward_ids:
                    # In a real app we'd filter by complaint ward_id. For now, scoping by dept or assignments
                    pass
                match_filter = {
                    "$or": dept_or
                }
                scope_note = f"Department operational scope ({department_id})"
            else:
                match_filter = {"assigned_authority_id": user_id}
                scope_note = "Assigned cases scope"

        total_complaints = await self.db["complaints"].count_documents(match_filter)

        status_pipeline = [
            {"$match": match_filter},
            {"$group": {"_id": "$status", "count": {"$sum": 1}}},
        ]
        status_cursor = await self.db["complaints"].aggregate(status_pipeline)
        status_res = await status_cursor.to_list(length=20)
        status_counts = [{"status": doc["_id"], "count": doc["count"]} for doc in status_res if doc.get("_id")]

        cat_pipeline = [
            {"$match": match_filter},
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
        ]
        cat_cursor = await self.db["complaints"].aggregate(cat_pipeline)
        cat_res = await cat_cursor.to_list(length=20)
        category_counts = [{"category": doc["_id"], "count": doc["count"]} for doc in cat_res if doc.get("_id")]

        unassigned_count = await self.db["assignments"].count_documents({"assigned_authority_id": {"$in": [None, ""]}})
        assigned_to_me_count = await self.db["assignments"].count_documents({"assigned_authority_id": user_id})

        in_progress_count = sum(c["count"] for c in status_counts if c["status"] == ComplaintStatus.IN_PROGRESS.value)
        resolved_count = sum(c["count"] for c in status_counts if c["status"] == ComplaintStatus.RESOLVED.value)
        closed_count = sum(c["count"] for c in status_counts if c["status"] == ComplaintStatus.CLOSED.value)

        recent_audit = await self.db["authority_audit_trail"].find(
            {}, sort=[("created_at", -1)], limit=10
        ).to_list(length=10)
        for r in recent_audit:
            if "_id" in r:
                r["_id"] = str(r["_id"])
            if isinstance(r.get("created_at"), datetime):
                r["created_at"] = r["created_at"].isoformat()

        integ_pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]
        integ_cursor = await self.db["external_integration_deliveries"].aggregate(integ_pipeline)
        integ_res = await integ_cursor.to_list(length=10)
        integration_status = {doc["_id"]: doc["count"] for doc in integ_res if doc.get("_id")}

        return {
            "total_complaints": total_complaints,
            "unassigned_count": unassigned_count,
            "assigned_to_me_count": assigned_to_me_count,
            "in_progress_count": in_progress_count,
            "resolved_count": resolved_count,
            "closed_count": closed_count,
            "status_counts": status_counts,
            "category_counts": category_counts,
            "recent_audit_activity": recent_audit,
            "integration_status": integration_status,
            "scope_note": scope_note,
        }

    async def get_authority_complaint_queue(
        self,
        user_id: str,
        role: str,
        department_id: Optional[str] = None,
        ward_ids: List[str] = None,
        status_filter: Optional[str] = None,
        category_filter: Optional[str] = None,
        assignment_filter: Optional[str] = None,
        search_query: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        """
        Server-side filtered, sorted, and paginated complaint queue for authority users.
        """
        query: Dict[str, Any] = {}

        if status_filter:
            query["status"] = status_filter
        if category_filter:
            query["category"] = category_filter

        if search_query:
            query["$or"] = [
                {"title": {"$regex": search_query, "$options": "i"}},
                {"description": {"$regex": search_query, "$options": "i"}},
                {"_id": {"$regex": search_query, "$options": "i"}},
            ]

        if role != "super_admin" and role != "admin":
            scope_constraints = []
            
            # Strict Ward Scoping
            if ward_ids:
                scope_constraints.append({"ward_id": {"$in": ward_ids}})
            
            # Strict Department Scoping (via Assignment table or direct Complaint property if it had one)
            # A complaint is assigned a department via the `assignments` collection.
            # To query complaints by department, we must find matching assignments first.
            if department_id:
                dept_assignments = await self.db["assignments"].find({"department_id": department_id}).to_list(length=10000)
                dept_comp_ids = [a["complaint_id"] for a in dept_assignments]
                scope_constraints.append({"_id": {"$in": dept_comp_ids}})

            if assignment_filter == "me":
                my_assignments = await self.db["assignments"].find({"assigned_authority_id": user_id}).to_list(length=10000)
                my_comp_ids = [a["complaint_id"] for a in my_assignments]
                scope_constraints.append({"_id": {"$in": my_comp_ids}})
            elif assignment_filter == "unassigned":
                assigned_ids = await self.db["assignments"].distinct("complaint_id", {"assigned_authority_id": {"$ne": None}})
                scope_constraints.append({"_id": {"$nin": assigned_ids}})

            if scope_constraints:
                query["$and"] = scope_constraints
        else:
            # Super Admin / Admin has global view, but can still use assignment_filter
            if assignment_filter == "me":
                assignments = await self.db["assignments"].find({"assigned_authority_id": user_id}).to_list(length=1000)
                comp_ids = [a["complaint_id"] for a in assignments]
                query["_id"] = {"$in": comp_ids}
            elif assignment_filter == "unassigned":
                assigned_ids = await self.db["assignments"].distinct("complaint_id", {"assigned_authority_id": {"$ne": None}})
                query["_id"] = {"$nin": assigned_ids}

        allowed_sorts = {"created_at", "status", "category", "updated_at", "priority_score"}
        target_sort = sort_by if sort_by in allowed_sorts else "created_at"
        sort_dir = -1 if sort_order.lower() == "desc" else 1

        total = await self.db["complaints"].count_documents(query)
        skip = max(0, (page - 1) * page_size)
        items = await self.db["complaints"].find(
            query, sort=[(target_sort, sort_dir)], skip=skip, limit=page_size
        ).to_list(length=page_size)

        for item in items:
            item["_id"] = str(item["_id"])
            if isinstance(item.get("created_at"), datetime):
                item["created_at"] = item["created_at"].isoformat()
            if isinstance(item.get("updated_at"), datetime):
                item["updated_at"] = item["updated_at"].isoformat()

            assignment = await self.db["assignments"].find_one({"complaint_id": item["_id"]})
            if assignment:
                item["department_id"] = assignment.get("department_id")
                item["assigned_authority_id"] = assignment.get("assigned_authority_id")

        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 1

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    async def get_authority_complaint_detail(
        self, complaint_id: str, user_id: str, role: str, department_id: Optional[str] = None, ward_ids: List[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Enriched complaint detail view for authority & admin users.
        """
        complaint = await self.db["complaints"].find_one({"_id": complaint_id})
        if not complaint:
            return None

        # Data Scoping Enforcement for detail view
        if role != "super_admin" and role != "admin":
            if ward_ids and complaint.get("ward_id") not in ward_ids:
                return None
            
            if department_id:
                assignment = await self.db["assignments"].find_one({"complaint_id": complaint_id})
                if not assignment or assignment.get("department_id") != department_id:
                    # Allow view if assigned directly to the authority
                    if not assignment or assignment.get("assigned_authority_id") != user_id:
                        return None

        complaint["_id"] = str(complaint["_id"])
        if isinstance(complaint.get("created_at"), datetime):
            complaint["created_at"] = complaint["created_at"].isoformat()

        evidence = await self.db["evidence"].find({"complaint_id": complaint_id}).to_list(length=50)
        for ev in evidence:
            ev["_id"] = str(ev["_id"])

        ai_analysis = await self.db["ai_analyses"].find({"complaint_id": complaint_id}).to_list(length=50)
        for ai in ai_analysis:
            ai["_id"] = str(ai["_id"])

        assignment = await self.db["assignments"].find_one({"complaint_id": complaint_id})
        if assignment:
            assignment["_id"] = str(assignment["_id"])

        status_history = await self.db["status_history"].find(
            {"complaint_id": complaint_id}, sort=[("created_at", 1)]
        ).to_list(length=50)
        for sh in status_history:
            sh["_id"] = str(sh["_id"])

        audit_trail = await self.db["authority_audit_trail"].find(
            {"complaint_id": complaint_id}, sort=[("created_at", -1)]
        ).to_list(length=50)
        for at in audit_trail:
            at["_id"] = str(at["_id"])
            if isinstance(at.get("created_at"), datetime):
                at["created_at"] = at["created_at"].isoformat()

        cluster = None
        if "cluster_id" in complaint:
            cluster = await self.db["incident_clusters"].find_one({"_id": complaint["cluster_id"]})
            if cluster:
                cluster["_id"] = str(cluster["_id"])

        external_delivery = await self.db["external_integration_deliveries"].find_one({"complaint_id": complaint_id})
        if external_delivery:
            external_delivery["_id"] = str(external_delivery["_id"])

        return {
            "complaint": complaint,
            "evidence": evidence,
            "ai_analysis": ai_analysis,
            "assignment": assignment,
            "status_history": status_history,
            "audit_trail": audit_trail,
            "routing_info": {"matched": True, "department_id": assignment.get("department_id") if assignment else "unassigned"},
            "intelligence": {"cluster": cluster} if cluster else None,
            "external_delivery": external_delivery,
        }

