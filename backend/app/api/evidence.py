"""
CivicPulse AI — Evidence & AI API Routes.
"""

import asyncio
import logging
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.database.mongodb import get_database
from app.dependencies.auth import RoleChecker, require_authenticated_user
from app.domain.auth_schemas import UserResponse
from app.domain.enums import UserRole
from app.domain.evidence_schemas import EvidenceResponse
from app.domain.ai_schemas import AIAnalysisResponse
from app.services.evidence_service import EvidenceService
from app.services.ai_service import AIService
from app.repositories.collections import AIAnalysisRepository

logger = logging.getLogger("civicpulse.api.evidence")

router = APIRouter(prefix="/api/v1/complaints", tags=["Evidence & AI"])
citizen_only = RoleChecker([UserRole.CITIZEN])

def get_evidence_service() -> EvidenceService:
    db = get_database()
    if db is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    return EvidenceService(db)

def get_ai_service() -> AIService:
    db = get_database()
    if db is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    return AIService(db)

@router.post("/{complaint_id}/evidence", response_model=EvidenceResponse, status_code=status.HTTP_201_CREATED)
async def upload_evidence(
    complaint_id: str,
    file: UploadFile = File(...),
    current_user: UserResponse = Depends(citizen_only),
    evidence_service: EvidenceService = Depends(get_evidence_service),
    ai_service: AIService = Depends(get_ai_service),
) -> EvidenceResponse:
    """
    Upload evidence for a complaint.
    Automatically triggers asynchronous AI analysis.
    """
    try:
        # Upload is synchronous in the request
        created_doc = await evidence_service.upload_evidence(complaint_id, current_user.id, file)
        
        # Fire off AI analysis asynchronously (fire-and-forget for MVP)
        # Using asyncio.create_task avoids blocking the HTTP response.
        # A more robust solution uses Redis/RQ.
        asyncio.create_task(ai_service.analyze_complaint(complaint_id))
        
        return EvidenceResponse(**created_doc)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=404, detail="Complaint not found") # Mask existence
    except RuntimeError as e:
        logger.error(str(e))
        raise HTTPException(status_code=500, detail="Failed to process upload")
    except Exception as e:
        logger.error(f"Unexpected error uploading evidence: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{complaint_id}/evidence", response_model=List[EvidenceResponse])
async def list_evidence(
    complaint_id: str,
    current_user: UserResponse = Depends(citizen_only),
    evidence_service: EvidenceService = Depends(get_evidence_service),
) -> List[EvidenceResponse]:
    """List evidence attached to a complaint."""
    # The service internally checks ownership
    items = await evidence_service.get_evidence_for_complaint(complaint_id, current_user.id)
    return [EvidenceResponse(**doc) for doc in items]


@router.get("/{complaint_id}/ai", response_model=List[AIAnalysisResponse])
async def get_ai_analysis(
    complaint_id: str,
    current_user: UserResponse = Depends(citizen_only),
) -> List[AIAnalysisResponse]:
    """Retrieve the AI analysis for a complaint. Ownership is checked."""
    db = get_database()
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    # 1. Verify ownership directly
    from app.repositories.collections import ComplaintRepository
    comp_repo = ComplaintRepository(db)
    complaint = await comp_repo.find_by_id(complaint_id)
    
    if not complaint or complaint.get("user_id") != current_user.id:
        raise HTTPException(status_code=404, detail="Complaint not found")
        
    ai_repo = AIAnalysisRepository(db)
    analyses = await ai_repo.find_by_complaint(complaint_id)
    return [AIAnalysisResponse(**doc) for doc in analyses]
