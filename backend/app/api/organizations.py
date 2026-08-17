import logging
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.database.mongodb import get_database
from app.dependencies.auth import RoleChecker, require_authenticated_user
from app.domain.auth_schemas import UserResponse
from app.domain.enums import UserRole, OrganizationVerificationStatus
from app.domain.organization_schemas import OrganizationCreateRequest, OrganizationResponse
from app.repositories.collections import OrganizationRepository, AuditLogRepository

logger = logging.getLogger("civicpulse.organizations")

router = APIRouter(prefix="/api/v1/organizations", tags=["Organizations"])

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

@router.post("", status_code=status.HTTP_201_CREATED, response_model=OrganizationResponse)
async def create_organization(
    request: OrganizationCreateRequest,
    current_user: UserResponse = Depends(require_authenticated_user)
):
    """Register a new organization (defaults to PENDING)."""
    db = get_database()
    repo = OrganizationRepository(db)
    
    doc = request.model_dump()
    doc["verification_status"] = OrganizationVerificationStatus.PENDING.value
    doc["created_at"] = datetime.utcnow()
    doc["updated_at"] = datetime.utcnow()
    
    org_id = await repo.insert_one(doc)
    await log_audit(current_user.id, "organization.created", "organization", org_id, {"name": request.name})
    
    res = await repo.find_by_id(org_id)
    res["id"] = str(res["_id"])
    return OrganizationResponse(**res)

@router.get("", response_model=List[OrganizationResponse])
async def list_organizations(
    current_user: UserResponse = Depends(require_authenticated_user)
):
    """List organizations."""
    db = get_database()
    repo = OrganizationRepository(db)
    
    query = {}
    if current_user.role == UserRole.CITIZEN:
        # Citizens only see verified orgs
        query["verification_status"] = OrganizationVerificationStatus.VERIFIED.value
        
    items = await repo.find_many(query, limit=100)
    for item in items:
        item["id"] = str(item["_id"])
    return [OrganizationResponse(**item) for item in items]

@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: str,
    current_user: UserResponse = Depends(require_authenticated_user)
):
    db = get_database()
    repo = OrganizationRepository(db)
    
    org = await repo.find_by_id(org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
        
    if current_user.role == UserRole.CITIZEN and org.get("verification_status") != OrganizationVerificationStatus.VERIFIED.value:
        raise HTTPException(status_code=403, detail="Organization is not public yet.")
        
    org["id"] = str(org["_id"])
    return OrganizationResponse(**org)
