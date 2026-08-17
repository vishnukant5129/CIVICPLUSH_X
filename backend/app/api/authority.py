"""
CivicPulse AI — Authority & Admin APIs.
"""

import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.config import get_settings
from app.database.mongodb import get_database
from app.dependencies.auth import RoleChecker, require_authenticated_user
from app.domain.auth_schemas import UserResponse
from app.domain.authority_dashboard_schemas import (
    AuthorityComplaintDetailResponse,
    AuthorityDashboardSummary,
    AuthorityQueueResponse,
)
from app.domain.enums import UserRole, ComplaintStatus, CivicCategory
from app.repositories.collections import ComplaintRepository, EvidenceRepository, DepartmentRepository, UserRepository
from app.services.authority_service import AuthorityService
from app.services.routing_service import RoutingService
from app.services.integration_adapter import GovernmentIntegrationAdapter

router = APIRouter(prefix="/api/v1/authority", tags=["Authority Operations"])

async def authority_only_check(current_user: UserResponse = Depends(require_authenticated_user)) -> UserResponse:
    if current_user.role == UserRole.CITIZEN:
        raise HTTPException(status_code=403, detail="Authority access required")
    return current_user

authority_only = authority_only_check

def get_auth_service() -> AuthorityService:
    db = get_database()
    return AuthorityService(db)


def get_routing_service() -> RoutingService:
    db = get_database()
    return RoutingService(db)


def get_integration_adapter() -> GovernmentIntegrationAdapter:
    db = get_database()
    return GovernmentIntegrationAdapter(db)


class AssignRequest(BaseModel):
    department_id: str
    authority_id: str


class StatusUpdateRequest(BaseModel):
    new_status: ComplaintStatus
    note: Optional[str] = None


@router.get("/dashboard/summary", response_model=AuthorityDashboardSummary)
async def get_dashboard_summary(
    current_user: UserResponse = Depends(authority_only),
    auth_service: AuthorityService = Depends(get_auth_service),
) -> AuthorityDashboardSummary:
    """
    Get aggregated operational statistics for authority & admin users.
    """
    summary = await auth_service.get_authority_dashboard_summary(
        user_id=current_user.id,
        role=current_user.role.value,
        department_id=getattr(current_user, "department_id", None),
        ward_ids=getattr(current_user, "ward_ids", []),
    )
    return AuthorityDashboardSummary(**summary)


@router.get("/complaints", response_model=AuthorityQueueResponse)
async def get_complaint_queue(
    status_filter: Optional[str] = Query(None, alias="status"),
    category_filter: Optional[str] = Query(None, alias="category"),
    assignment_filter: Optional[str] = Query(None, alias="assignment"),
    search: Optional[str] = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: UserResponse = Depends(authority_only),
    auth_service: AuthorityService = Depends(get_auth_service),
) -> AuthorityQueueResponse:
    """
    Server-side filtered, sorted, and paginated complaint queue for authority users.
    """
    res = await auth_service.get_authority_complaint_queue(
        user_id=current_user.id,
        role=current_user.role.value,
        department_id=getattr(current_user, "department_id", None),
        ward_ids=getattr(current_user, "ward_ids", []),
        status_filter=status_filter,
        category_filter=category_filter,
        assignment_filter=assignment_filter,
        search_query=search,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )
    return AuthorityQueueResponse(**res)


@router.get("/complaints/{complaint_id}", response_model=AuthorityComplaintDetailResponse)
async def get_complaint_detail(
    complaint_id: str,
    current_user: UserResponse = Depends(authority_only),
    auth_service: AuthorityService = Depends(get_auth_service),
) -> AuthorityComplaintDetailResponse:
    """
    Get enriched complaint detail view including evidence, AI analysis, routing,
    status history, audit trail, and government integration status.
    """
    detail = await auth_service.get_authority_complaint_detail(
        complaint_id=complaint_id,
        user_id=current_user.id,
        role=current_user.role.value,
        department_id=getattr(current_user, "department_id", None),
        ward_ids=getattr(current_user, "ward_ids", []),
    )
    if not detail:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return AuthorityComplaintDetailResponse(**detail)


@router.get("/evidence/{evidence_id}/download")
async def download_evidence(
    evidence_id: str,
    current_user: UserResponse = Depends(require_authenticated_user),
):
    """
    Secure, protected file download for evidence files.
    Enforces ownership/scope authorization.
    """
    db = get_database()
    evidence_repo = EvidenceRepository(db)
    evidence = await evidence_repo.find_by_id(evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence record not found")

    complaint_id = evidence.get("complaint_id")
    complaint_repo = ComplaintRepository(db)
    complaint = await complaint_repo.find_by_id(complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    if current_user.role == UserRole.CITIZEN:
        if complaint.get("user_id") != current_user.id:
            raise HTTPException(status_code=404, detail="Evidence record not found")
    elif current_user.role in [UserRole.AUTHORITY, UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        # Validate Authority Scope
        auth_service = AuthorityService(db)
        has_access = await auth_service.get_authority_complaint_detail(
            complaint_id=complaint_id,
            user_id=current_user.id,
            role=current_user.role.value,
            department_id=getattr(current_user, "department_id", None),
            ward_ids=getattr(current_user, "ward_ids", []),
        )
        if not has_access:
             raise HTTPException(status_code=404, detail="Evidence record not found")
    else:
        raise HTTPException(status_code=403, detail="Access denied")

    storage_key = evidence.get("storage_key")
    if not storage_key:
        raise HTTPException(status_code=404, detail="File path invalid")

    settings = get_settings()
    storage_dir = settings.storage_path
    
    # Path traversal protection
    norm_storage_key = os.path.normpath(storage_key)
    if norm_storage_key.startswith(".."):
        raise HTTPException(status_code=400, detail="Invalid storage path")
        
    absolute_path = os.path.join(storage_dir, norm_storage_key)
    if not os.path.isfile(absolute_path):
        raise HTTPException(status_code=404, detail="Evidence file missing on server storage")

    return FileResponse(
        path=absolute_path,
        media_type=evidence.get("mime_type", "application/octet-stream"),
        filename=evidence.get("original_filename", "evidence_file"),
    )


@router.get("/departments")
async def list_departments(
    current_user: UserResponse = Depends(authority_only),
):
    """List active departments for authority routing and assignment."""
    db = get_database()
    dept_repo = DepartmentRepository(db)
    depts = await dept_repo.find_active()
    return [{"id": str(d.get("_id")), "department_id": d.get("department_id", str(d.get("_id"))), "name": d.get("name", d.get("code", "Dept"))} for d in depts]


@router.post("/complaints/{complaint_id}/assign")
async def assign_complaint(
    complaint_id: str,
    req: AssignRequest,
    current_user: UserResponse = Depends(authority_only),
    auth_service: AuthorityService = Depends(get_auth_service),
):
    # Data Scope Enforcement
    detail = await auth_service.get_authority_complaint_detail(
        complaint_id=complaint_id,
        user_id=current_user.id,
        role=current_user.role.value,
        department_id=getattr(current_user, "department_id", None),
        ward_ids=getattr(current_user, "ward_ids", []),
    )
    if not detail:
        raise HTTPException(status_code=404, detail="Complaint not found")

    try:
        success = await auth_service.assign_complaint(complaint_id, req.authority_id, req.department_id, current_user.id)
        if not success:
            raise HTTPException(status_code=404, detail="Complaint not found")
        return {"status": "success", "message": "Complaint successfully assigned."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/complaints/{complaint_id}/status")
async def update_complaint_status(
    complaint_id: str,
    req: StatusUpdateRequest,
    current_user: UserResponse = Depends(authority_only),
    auth_service: AuthorityService = Depends(get_auth_service),
):
    # Data Scope Enforcement
    detail = await auth_service.get_authority_complaint_detail(
        complaint_id=complaint_id,
        user_id=current_user.id,
        role=current_user.role.value,
        department_id=getattr(current_user, "department_id", None),
        ward_ids=getattr(current_user, "ward_ids", []),
    )
    if not detail:
        raise HTTPException(status_code=404, detail="Complaint not found")

    try:
        success = await auth_service.update_status(complaint_id, current_user.id, req.new_status, req.note)
        if not success:
            raise HTTPException(status_code=404, detail="Complaint not found")
        return {"status": "success", "message": "Complaint status successfully updated."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/complaints/{complaint_id}/route")
async def route_complaint(
    complaint_id: str,
    current_user: UserResponse = Depends(authority_only),
    routing_service: RoutingService = Depends(get_routing_service),
    auth_service: AuthorityService = Depends(get_auth_service),
):
    """Manually trigger routing for a complaint based on data."""
    # Data Scope Enforcement
    detail = await auth_service.get_authority_complaint_detail(
        complaint_id=complaint_id,
        user_id=current_user.id,
        role=current_user.role.value,
        department_id=getattr(current_user, "department_id", None),
        ward_ids=getattr(current_user, "ward_ids", []),
    )
    if not detail:
        raise HTTPException(status_code=404, detail="Complaint not found")

    db = routing_service.db
    complaint = await db["complaints"].find_one({"_id": complaint_id})
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
        
    category = complaint.get("category", "")
    jurisdiction_id = None
    
    result = await routing_service.route_complaint(complaint_id, category, jurisdiction_id)
    return result


@router.post("/complaints/{complaint_id}/external-delivery")
async def trigger_external_delivery(
    complaint_id: str,
    current_user: UserResponse = Depends(authority_only),
    adapter: GovernmentIntegrationAdapter = Depends(get_integration_adapter),
    auth_service: AuthorityService = Depends(get_auth_service),
):
    """
    Attempts to deliver the complaint to a downstream municipal provider.
    Returns honest representation of integration configuration status.
    """
    # Data Scope Enforcement
    detail = await auth_service.get_authority_complaint_detail(
        complaint_id=complaint_id,
        user_id=current_user.id,
        role=current_user.role.value,
        department_id=getattr(current_user, "department_id", None),
        ward_ids=getattr(current_user, "ward_ids", []),
    )
    if not detail:
        raise HTTPException(status_code=404, detail="Complaint not found")

    db = adapter.db
    complaint = await db["complaints"].find_one({"_id": complaint_id})
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
        
    result = await adapter.deliver_complaint(complaint_id, complaint)
    return result
