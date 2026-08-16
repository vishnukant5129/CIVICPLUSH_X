"""
CivicPulse AI — Complaint API Routes.

Handles complaint creation, listing, and detail views for citizens.
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.database.mongodb import get_database
from app.dependencies.auth import require_authenticated_user, RoleChecker
from app.domain.auth_schemas import UserResponse
from app.domain.complaint_schemas import (
    ComplaintCreateRequest,
    ComplaintResponse,
    StatusHistoryResponse,
)
from app.domain.enums import UserRole
from app.services.complaint_service import ComplaintService

logger = logging.getLogger("civicpulse.api.complaints")

router = APIRouter(prefix="/api/v1/complaints", tags=["Complaints"])

# All complaint creation/viewing routes here are for CITIZENs primarily.
citizen_only = RoleChecker([UserRole.CITIZEN])


def get_complaint_service() -> ComplaintService:
    db = get_database()
    if db is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    return ComplaintService(db)


@router.post("/", response_model=ComplaintResponse, status_code=status.HTTP_201_CREATED)
async def create_complaint(
    request: ComplaintCreateRequest,
    current_user: UserResponse = Depends(citizen_only),
    service: ComplaintService = Depends(get_complaint_service),
) -> ComplaintResponse:
    """
    Create a new civic complaint.
    The complaint is permanently associated with the authenticated user.
    """
    try:
        created_doc = await service.create_complaint(current_user.id, request)
        return ComplaintResponse(**created_doc)
    except Exception as e:
        logger.error(f"Error creating complaint: {e}")
        raise HTTPException(status_code=500, detail="Failed to create complaint")


@router.get("/my", response_model=List[ComplaintResponse])
async def list_my_complaints(
    current_user: UserResponse = Depends(citizen_only),
    service: ComplaintService = Depends(get_complaint_service),
) -> List[ComplaintResponse]:
    """
    List all complaints owned by the authenticated user.
    """
    complaints = await service.get_user_complaints(current_user.id)
    return [ComplaintResponse(**doc) for doc in complaints]


@router.get("/{complaint_id}", response_model=ComplaintResponse)
async def get_complaint(
    complaint_id: str,
    current_user: UserResponse = Depends(citizen_only),
    service: ComplaintService = Depends(get_complaint_service),
) -> ComplaintResponse:
    """
    Get details of a specific complaint.
    Returns 404 if the complaint does not exist OR if it belongs to another user.
    """
    complaint = await service.get_complaint_detail(complaint_id, current_user.id)
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found.",
        )
    return ComplaintResponse(**complaint)


@router.get("/{complaint_id}/history", response_model=List[StatusHistoryResponse])
async def get_complaint_history(
    complaint_id: str,
    current_user: UserResponse = Depends(citizen_only),
    service: ComplaintService = Depends(get_complaint_service),
) -> List[StatusHistoryResponse]:
    """
    Get the status history of a specific complaint.
    Returns 404 if the complaint does not exist OR if it belongs to another user.
    """
    history = await service.get_complaint_status_history(complaint_id, current_user.id)
    if history is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found.",
        )
    return [StatusHistoryResponse(**doc) for doc in history]
