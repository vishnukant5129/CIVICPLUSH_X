"""
CivicPulse AI — Intelligence API Routes.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks

from app.database.mongodb import get_database
from app.dependencies.auth import RoleChecker
from app.domain.auth_schemas import UserResponse
from app.domain.enums import UserRole
from app.domain.intelligence_schemas import IntelligenceResponse
from app.services.intelligence_service import IntelligenceService
from app.repositories.collections import ComplaintRepository

router = APIRouter(prefix="/api/v1/intelligence", tags=["Intelligence"])
citizen_only = RoleChecker([UserRole.CITIZEN])

def get_intelligence_service() -> IntelligenceService:
    db = get_database()
    if db is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    return IntelligenceService(db)

@router.get("/complaints/{complaint_id}", response_model=IntelligenceResponse)
async def get_complaint_intelligence(
    complaint_id: str,
    current_user: UserResponse = Depends(citizen_only),
    intelligence_service: IntelligenceService = Depends(get_intelligence_service),
) -> IntelligenceResponse:
    """
    Retrieve Intelligence data for a specific complaint.
    Security: Ensures the citizen owns the complaint before returning relation mapping.
    """
    db = intelligence_service.db
    comp_repo = ComplaintRepository(db)
    
    complaint = await comp_repo.find_by_id(complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
        
    # Isolation: Citizens can only see intelligence for their own complaints.
    if complaint.get("user_id") != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this intelligence.")
        
    data = await intelligence_service.get_intelligence_for_complaint(complaint_id)
    return IntelligenceResponse(**data)

@router.post("/complaints/{complaint_id}/process", status_code=202)
async def trigger_intelligence_processing(
    complaint_id: str,
    background_tasks: BackgroundTasks,
    current_user: UserResponse = Depends(citizen_only),
    intelligence_service: IntelligenceService = Depends(get_intelligence_service),
):
    """
    Manually trigger intelligence processing for a complaint.
    This safely triggers embedding generation and candidate matching in the background.
    """
    db = intelligence_service.db
    comp_repo = ComplaintRepository(db)
    
    complaint = await comp_repo.find_by_id(complaint_id)
    if not complaint or complaint.get("user_id") != current_user.id:
        raise HTTPException(status_code=404, detail="Complaint not found")
        
    # We use FastAPI BackgroundTasks as a lightweight durable queue for the HTTP request lifecycle.
    # Note: Phase 6 limitation applies (lost on server restart).
    background_tasks.add_task(intelligence_service.process_intelligence, complaint_id)
    
    return {"status": "accepted", "message": "Intelligence processing scheduled."}
