import logging
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.database.mongodb import get_database
from app.dependencies.auth import RoleChecker, require_authenticated_user
from app.domain.auth_schemas import UserResponse
from app.domain.enums import UserRole, CivicProjectStatus, MatchRequestStatus
from pydantic import BaseModel
from app.domain.project_schemas import (
    CivicProjectCreateRequest,
    CivicProjectResponse,
    ResourceMatchRequestCreate,
    ResourceMatchRequestResponse,
)
from app.repositories.collections import CivicProjectRepository, ResourceMatchRequestRepository, AuditLogRepository

logger = logging.getLogger("civicpulse.projects")

router = APIRouter(prefix="/api/v1/civic-projects", tags=["Civic Projects"])

authority_admin_only = RoleChecker([
    UserRole.SUPER_ADMIN, 
    UserRole.MUNICIPAL_ADMIN, UserRole.DEPARTMENT_HEAD, UserRole.WARD_SUPERVISOR,
    UserRole.AUTHORITY_OFFICER, UserRole.FIELD_INSPECTOR
])

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

@router.post("", status_code=status.HTTP_201_CREATED, response_model=CivicProjectResponse)
async def create_civic_project(
    request: CivicProjectCreateRequest,
    current_user: UserResponse = Depends(authority_admin_only)
):
    """Create a new verified Civic Project (Authority only)."""
    db = get_database()
    repo = CivicProjectRepository(db)
    
    project_code = f"CPX-{uuid.uuid4().hex[:8].upper()}"
    
    doc = request.model_dump()
    doc["project_code"] = project_code
    doc["status"] = CivicProjectStatus.IDENTIFIED.value
    doc["verification_status"] = "VERIFIED"
    doc["created_at"] = datetime.utcnow()
    doc["updated_at"] = datetime.utcnow()
    
    project_id = await repo.insert_one(doc)
    await log_audit(current_user.id, "project.created", "civic_project", project_id, {"code": project_code})
    
    res = await repo.find_by_id(project_id)
    res["id"] = str(res["_id"])
    return CivicProjectResponse(**res)


@router.get("", response_model=List[CivicProjectResponse])
async def list_civic_projects(
    status_filter: Optional[str] = Query(None, alias="status"),
    ward_filter: Optional[str] = Query(None, alias="ward_id"),
    current_user: UserResponse = Depends(require_authenticated_user)
):
    """
    List civic projects.
    Citizens can only see VERIFIED and public states.
    """
    db = get_database()
    repo = CivicProjectRepository(db)
    
    query = {}
    if status_filter:
        query["status"] = status_filter
    if ward_filter:
        query["ward_id"] = ward_filter
        
    if current_user.role == UserRole.CITIZEN:
        # Hide unverified or internal projects
        query["verification_status"] = "VERIFIED"
        
    items = await repo.find_many(query, limit=100)
    for item in items:
        item["id"] = str(item["_id"])
    return [CivicProjectResponse(**item) for item in items]


@router.get("/{project_id}", response_model=CivicProjectResponse)
async def get_civic_project(
    project_id: str,
    current_user: UserResponse = Depends(require_authenticated_user)
):
    db = get_database()
    repo = CivicProjectRepository(db)
    
    project = await repo.find_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    if current_user.role == UserRole.CITIZEN and project.get("verification_status") != "VERIFIED":
        raise HTTPException(status_code=403, detail="Project is not public yet.")
        
    project["id"] = str(project["_id"])
    return CivicProjectResponse(**project)


@router.post("/{project_id}/interest", status_code=status.HTTP_201_CREATED, response_model=ResourceMatchRequestResponse)
async def express_interest(
    project_id: str,
    request: ResourceMatchRequestCreate,
    current_user: UserResponse = Depends(require_authenticated_user)
):
    """Express interest from an organization."""
    db = get_database()
    repo = ResourceMatchRequestRepository(db)
    
    # Validation
    if project_id != request.project_id:
        raise HTTPException(status_code=400, detail="Project ID mismatch")
        
    doc = request.model_dump()
    doc["status"] = MatchRequestStatus.SUBMITTED.value
    doc["created_at"] = datetime.utcnow()
    doc["updated_at"] = datetime.utcnow()
    
    match_id = await repo.insert_one(doc)
    await log_audit(current_user.id, "match_request.submitted", "match_request", match_id, {"project_id": project_id})
    
    res = await repo.find_by_id(match_id)
    res["id"] = str(res["_id"])
    return ResourceMatchRequestResponse(**res)


class ProjectStatusUpdate(BaseModel):
    status: CivicProjectStatus

@router.patch("/{project_id}/status")
async def update_project_status(
    project_id: str,
    request: ProjectStatusUpdate,
    current_user: UserResponse = Depends(authority_admin_only)
):
    db = get_database()
    repo = CivicProjectRepository(db)
    
    project = await repo.find_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    await repo.update_one(project_id, {"$set": {"status": request.status.value, "updated_at": datetime.utcnow()}})
    await log_audit(current_user.id, "project.status_update", "civic_project", project_id, {"status": request.status.value})
    return {"status": "success"}

class OutcomeVerificationRequest(BaseModel):
    outcome_status: str
    inspection_notes: Optional[str] = None

@router.post("/{project_id}/verify-outcome")
async def verify_project_outcome(
    project_id: str,
    request: OutcomeVerificationRequest,
    current_user: UserResponse = Depends(authority_admin_only)
):
    db = get_database()
    repo = CivicProjectRepository(db)
    
    project = await repo.find_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    updates = {
        "status": CivicProjectStatus.OUTCOME_VERIFIED.value,
        "impact_summary": request.inspection_notes or project.get("impact_summary"),
        "updated_at": datetime.utcnow()
    }
    await repo.update_one(project_id, {"$set": updates})
    await log_audit(current_user.id, "project.outcome_verified", "civic_project", project_id, {"outcome_status": request.outcome_status})
    return {"status": "success"}
