import logging
from typing import List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.database.mongodb import get_database
from app.dependencies.auth import RoleChecker
from app.domain.auth_schemas import UserResponse
from app.domain.enums import UserRole, UserStatus, DepartmentStatus
from app.domain.admin_schemas import (
    CreateDepartmentRequest,
    CreateWardRequest,
    CreateAuthorityRequest,
    AuthorityUpdateScopeRequest,
    UpdateDepartmentRequest,
    UpdateWardRequest,
    CreateRoutingRuleRequest,
    UpdateRoutingRuleRequest,
)
from app.repositories.collections import (
    UserRepository,
    DepartmentRepository,
    WardRepository,
    AuditLogRepository,
    OrganizationRepository,
    CivicProjectRepository,
    IncidentClusterRepository,
    ResourceMatchRequestRepository,
)
from app.domain.enums import ComplaintStatus
from app.repositories.base import DuplicateDocumentError
from datetime import datetime

logger = logging.getLogger("civicpulse.admin")

router = APIRouter(prefix="/api/v1/admin", tags=["Admin Control Center"])

super_admin_only = RoleChecker([UserRole.SUPER_ADMIN, UserRole.MUNICIPAL_ADMIN])

async def log_audit(actor_id: str, action: str, resource_type: str, resource_id: str, metadata: dict = None):
    db = get_database()
    if db:
        repo = AuditLogRepository(db)
        await repo.insert_one({
            "actor_id": actor_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "metadata": metadata or {}
        })

@router.get("/overview")
async def get_admin_overview(current_user: UserResponse = Depends(super_admin_only)):
    db = get_database()
    
    # Complaints
    complaints_coll = db["complaints"]
    total_cases = await complaints_coll.count_documents({})
    in_progress = await complaints_coll.count_documents({"status": ComplaintStatus.IN_PROGRESS.value})
    resolved = await complaints_coll.count_documents({"status": ComplaintStatus.RESOLVED.value})
    closed = await complaints_coll.count_documents({"status": ComplaintStatus.CLOSED.value})
    
    # Assignments
    assignments_coll = db["assignments"]
    assigned = await assignments_coll.count_documents({"assigned_authority_id": {"$ne": None}})
    unassigned = total_cases - assigned # simplification
    
    # Admin metrics
    users_coll = db["users"]
    active_auths = await users_coll.count_documents({"role": {"$ne": "citizen"}, "status": "active"})
    pending_auths = await users_coll.count_documents({"role": {"$ne": "citizen"}, "status": "inactive"})
    
    depts_coll = db["departments"]
    active_depts = await depts_coll.count_documents({"status": "active"})
    
    wards_coll = db["wards"]
    active_wards = await wards_coll.count_documents({"status": "active"})
    
    projects_coll = db["civic_projects"]
    open_projects = await projects_coll.count_documents({"status": {"$nin": ["completed", "outcome_verified"]}})
    
    orgs_coll = db["organizations"]
    verified_orgs = await orgs_coll.count_documents({"verification_status": "verified"})
    
    return {
        "operational": {
            "total_cases": total_cases,
            "unassigned": max(0, unassigned),
            "assigned": assigned,
            "in_progress": in_progress,
            "resolved": resolved,
            "closed": closed
        },
        "administrative": {
            "active_authorities": active_auths,
            "pending_authorities": pending_auths,
            "active_departments": active_depts,
            "active_wards": active_wards,
            "open_civic_projects": open_projects,
            "verified_organizations": verified_orgs
        }
    }

@router.post("/departments", status_code=status.HTTP_201_CREATED)
async def create_department(
    request: CreateDepartmentRequest,
    current_user: UserResponse = Depends(super_admin_only)
):
    """Create a new department."""
    db = get_database()
    repo = DepartmentRepository(db)
    
    doc = {
        "name": request.name,
        "code": request.code,
        "description": request.description,
        "status": DepartmentStatus.ACTIVE.value
    }
    
    try:
        dept_id = await repo.insert_one(doc)
        await log_audit(current_user.id, "department.created", "department", dept_id, {"code": request.code})
        return await repo.find_by_id(dept_id)
    except DuplicateDocumentError:
        raise HTTPException(status_code=409, detail="Department code already exists.")

@router.get("/departments")
async def list_departments(current_user: UserResponse = Depends(super_admin_only)):
    db = get_database()
    repo = DepartmentRepository(db)
    return await repo.find_many({}, limit=100)

@router.put("/departments/{dept_id}")
async def update_department(
    dept_id: str,
    request: UpdateDepartmentRequest,
    current_user: UserResponse = Depends(super_admin_only)
):
    db = get_database()
    repo = DepartmentRepository(db)
    updates = request.model_dump(exclude_unset=True)
    if updates:
        updates["updated_at"] = datetime.utcnow()
        await repo.update_one(dept_id, {"$set": updates})
        await log_audit(current_user.id, "department.updated", "department", dept_id, updates)
    return await repo.find_by_id(dept_id)

@router.delete("/departments/{dept_id}")
async def delete_department(dept_id: str, current_user: UserResponse = Depends(super_admin_only)):
    db = get_database()
    repo = DepartmentRepository(db)
    await repo.update_one(dept_id, {"$set": {"status": DepartmentStatus.INACTIVE.value, "updated_at": datetime.utcnow()}})
    await log_audit(current_user.id, "department.deactivated", "department", dept_id, {})
    return {"status": "success"}

@router.post("/wards", status_code=status.HTTP_201_CREATED)
async def create_ward(
    request: CreateWardRequest,
    current_user: UserResponse = Depends(super_admin_only)
):
    """Create a new ward."""
    db = get_database()
    repo = WardRepository(db)
    
    doc = {
        "name": request.name,
        "code": request.code,
        "description": request.description,
        "status": DepartmentStatus.ACTIVE.value
    }
    
    try:
        ward_id = await repo.insert_one(doc)
        await log_audit(current_user.id, "ward.created", "ward", ward_id, {"code": request.code})
        return await repo.find_by_id(ward_id)
    except DuplicateDocumentError:
        raise HTTPException(status_code=409, detail="Ward code already exists.")

@router.get("/wards")
async def list_wards(current_user: UserResponse = Depends(super_admin_only)):
    db = get_database()
    repo = WardRepository(db)
    return await repo.find_many({}, limit=100)

@router.put("/wards/{ward_id}")
async def update_ward(
    ward_id: str,
    request: UpdateWardRequest,
    current_user: UserResponse = Depends(super_admin_only)
):
    db = get_database()
    repo = WardRepository(db)
    updates = request.model_dump(exclude_unset=True)
    if updates:
        updates["updated_at"] = datetime.utcnow()
        await repo.update_one(ward_id, {"$set": updates})
        await log_audit(current_user.id, "ward.updated", "ward", ward_id, updates)
    return await repo.find_by_id(ward_id)

@router.delete("/wards/{ward_id}")
async def delete_ward(ward_id: str, current_user: UserResponse = Depends(super_admin_only)):
    db = get_database()
    repo = WardRepository(db)
    await repo.update_one(ward_id, {"$set": {"status": DepartmentStatus.INACTIVE.value, "updated_at": datetime.utcnow()}})
    await log_audit(current_user.id, "ward.deactivated", "ward", ward_id, {})
    return {"status": "success"}

@router.post("/authorities", status_code=status.HTTP_201_CREATED)
async def create_authority(
    request: CreateAuthorityRequest,
    current_user: UserResponse = Depends(super_admin_only)
):
    """Provision a new authority user. Status defaults to ACTIVE (Pending Google Login)."""
    db = get_database()
    repo = UserRepository(db)
    
    # Check if exists
    existing = await repo.find_by_email(request.email)
    if existing:
        raise HTTPException(status_code=409, detail="User with this email already exists.")
        
    doc = {
        "email": request.email,
        "normalized_email": request.email.lower(),
        "display_name": request.display_name,
        "role": request.role.value,
        "department_id": request.department_id,
        "ward_ids": request.ward_ids,
        "permissions": request.permissions,
        "status": UserStatus.ACTIVE.value,
        "google_sub": None,
        "password_hash": None,
    }
    
    try:
        user_id = await repo.insert_one(doc)
        await log_audit(current_user.id, "authority.created", "user", user_id, {"role": request.role.value})
        return await repo.find_by_id(user_id)
    except DuplicateDocumentError:
        raise HTTPException(status_code=409, detail="Duplicate constraint failed.")

@router.put("/authorities/{user_id}")
async def update_authority_scope(
    user_id: str,
    request: AuthorityUpdateScopeRequest,
    current_user: UserResponse = Depends(super_admin_only)
):
    """Update an authority's scope or status."""
    db = get_database()
    repo = UserRepository(db)
    
    existing = await repo.find_by_id(user_id)
    if not existing:
        raise HTTPException(status_code=404, detail="User not found")
        
    updates = {}
    if request.role is not None:
        updates["role"] = request.role.value
    if request.department_id is not None:
        updates["department_id"] = request.department_id
    if request.ward_ids is not None:
        updates["ward_ids"] = request.ward_ids
    if request.permissions is not None:
        updates["permissions"] = request.permissions
    if request.status is not None:
        updates["status"] = request.status.value
        
    if not updates:
        return existing
        
    await repo.update_one(user_id, {"$set": updates})
    await log_audit(current_user.id, "authority.updated", "user", user_id, updates)
    return await repo.find_by_id(user_id)

@router.get("/authorities")
async def list_authorities(current_user: UserResponse = Depends(super_admin_only)):
    db = get_database()
    repo = UserRepository(db)
    # Return all users who are not citizens
    return await repo.find_many({"role": {"$ne": UserRole.CITIZEN.value}}, limit=500)


@router.put("/organizations/{org_id}/verify")
async def verify_organization(
    org_id: str,
    status: str,
    current_user: UserResponse = Depends(super_admin_only)
):
    """Verify, Suspend, or Reject an organization."""
    db = get_database()
    repo = OrganizationRepository(db)
    
    org = await repo.find_by_id(org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
        
    await repo.update_one(org_id, {"$set": {"verification_status": status, "updated_at": datetime.utcnow()}})
    await log_audit(current_user.id, "organization.verified", "organization", org_id, {"status": status})
    return {"status": "success"}


@router.put("/civic-projects/{project_id}/verify")
async def verify_civic_project(
    project_id: str,
    status: str,
    current_user: UserResponse = Depends(super_admin_only)
):
    """Update verification status of a civic project."""
    db = get_database()
    repo = CivicProjectRepository(db)
    
    project = await repo.find_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    await repo.update_one(project_id, {"$set": {"verification_status": status, "updated_at": datetime.utcnow()}})
    await log_audit(current_user.id, "project.verified", "civic_project", project_id, {"status": status})
    return {"status": "success"}

@router.get("/audit")
async def get_audit_logs(limit: int = 50, current_user: UserResponse = Depends(super_admin_only)):
    db = get_database()
    repo = AuditLogRepository(db)
    return await repo.find_many({}, sort=[("created_at", -1)], limit=limit)

@router.get("/roles")
async def get_roles(current_user: UserResponse = Depends(super_admin_only)):
    return {
        "roles": [r.value for r in UserRole],
        "permissions_map": {
            UserRole.SUPER_ADMIN.value: ["all"],
            UserRole.MUNICIPAL_ADMIN.value: ["manage_users", "manage_wards", "manage_departments", "manage_projects"],
            UserRole.AUTHORITY_OFFICER.value: ["view_cases", "update_status", "add_notes"],
            UserRole.CITIZEN.value: ["create_complaint", "view_own_complaints"]
        }
    }

@router.get("/clusters")
async def get_clusters(current_user: UserResponse = Depends(super_admin_only)):
    db = get_database()
    repo = IncidentClusterRepository(db)
    return await repo.find_many({}, sort=[("complaint_count", -1)], limit=100)

@router.get("/matching")
async def get_match_requests(current_user: UserResponse = Depends(super_admin_only)):
    db = get_database()
    repo = ResourceMatchRequestRepository(db)
    return await repo.find_many({}, sort=[("created_at", -1)], limit=100)

@router.get("/settings")
async def get_settings_admin(current_user: UserResponse = Depends(super_admin_only)):
    return {
        "routing_configuration": "auto",
        "notification_preferences": "all",
        "feature_flags": {"civicpulse_x_enabled": True},
        "default_priority": "MEDIUM",
        "verification_required": True
    }

@router.get("/routing-rules")
async def list_routing_rules(current_user: UserResponse = Depends(super_admin_only)):
    db = get_database()
    cursor = db["routing_rules"].find().sort("priority", 1)
    rules = await cursor.to_list(length=100)
    for r in rules:
        r["_id"] = str(r["_id"])
    return rules

@router.post("/routing-rules", status_code=status.HTTP_201_CREATED)
async def create_routing_rule(
    request: CreateRoutingRuleRequest,
    current_user: UserResponse = Depends(super_admin_only)
):
    db = get_database()
    
    # Validate dept
    dept = await DepartmentRepository(db).find_by_id(request.department_id)
    if not dept:
        raise HTTPException(status_code=400, detail="Department not found")
        
    # Validate ward if provided
    if request.jurisdiction:
        ward = await WardRepository(db).find_by_id(request.jurisdiction)
        if not ward:
            raise HTTPException(status_code=400, detail="Ward not found")

    doc = request.model_dump()
    doc["created_at"] = datetime.utcnow()
    
    result = await db["routing_rules"].insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    
    await log_audit(current_user.id, "routing_rule.created", "routing_rule", doc["_id"], {"category": request.category})
    return doc

@router.put("/routing-rules/{rule_id}")
async def update_routing_rule(
    rule_id: str,
    request: UpdateRoutingRuleRequest,
    current_user: UserResponse = Depends(super_admin_only)
):
    from bson import ObjectId
    db = get_database()
    updates = request.model_dump(exclude_unset=True)
    if updates:
        await db["routing_rules"].update_one({"_id": ObjectId(rule_id)}, {"$set": updates})
        await log_audit(current_user.id, "routing_rule.updated", "routing_rule", rule_id, updates)
    return {"status": "success"}

@router.delete("/routing-rules/{rule_id}")
async def delete_routing_rule(rule_id: str, current_user: UserResponse = Depends(super_admin_only)):
    from bson import ObjectId
    db = get_database()
    await db["routing_rules"].update_one({"_id": ObjectId(rule_id)}, {"$set": {"active": False}})
    await log_audit(current_user.id, "routing_rule.deactivated", "routing_rule", rule_id, {})
    return {"status": "success"}
