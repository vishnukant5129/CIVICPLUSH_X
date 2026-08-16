"""
CivicPulse AI — Predictive Intelligence API.

Routes providing predictive analytics, category volume forecasting,
trend direction, spatial hotspot risk, and statistical evaluation.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status

from app.database.mongodb import get_database
from app.dependencies.auth import require_authenticated_user
from app.domain.auth_schemas import UserResponse
from app.domain.enums import UserRole
from app.domain.prediction_schemas import PredictionResponse
from app.services.predictive_service import PredictiveService

router = APIRouter(prefix="/api/v1/predictions", tags=["Predictive Intelligence"])


def get_predictive_service() -> PredictiveService:
    db = get_database()
    return PredictiveService(db)


@router.get("/summary", response_model=PredictionResponse)
async def get_prediction_summary(
    current_user: UserResponse = Depends(require_authenticated_user),
    service: PredictiveService = Depends(get_predictive_service),
):
    """
    Get overall predictive intelligence summary including trend directions,
    time-series forecasting, and data sufficiency state.
    """
    return await service.get_summary()


@router.get("/trends", response_model=PredictionResponse)
async def get_prediction_trends(
    current_user: UserResponse = Depends(require_authenticated_user),
    service: PredictiveService = Depends(get_predictive_service),
):
    """
    Get category volume trends and time-series forecasts.
    """
    return await service.get_trends()


@router.get("/hotspots", response_model=PredictionResponse)
async def get_prediction_hotspots(
    current_user: UserResponse = Depends(require_authenticated_user),
    service: PredictiveService = Depends(get_predictive_service),
):
    """
    Get spatial grid hotspot risk analysis.
    Restricted to authority operational personnel and system administrators.
    """
    allowed_roles = {UserRole.AUTHORITY, UserRole.ADMIN}
    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted. Operational spatial hotspot risk data requires authority or admin credentials.",
        )
    return await service.get_hotspots()


@router.post("/generate", response_model=PredictionResponse)
async def generate_predictions(
    current_user: UserResponse = Depends(require_authenticated_user),
    service: PredictiveService = Depends(get_predictive_service),
):
    """
    Trigger manual generation of predictive models on persisted complaint data.
    Restricted to authority or admin users.
    """
    allowed_roles = {UserRole.AUTHORITY, UserRole.ADMIN}
    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only authority or admin users can trigger predictive intelligence pipeline execution.",
        )
    return await service.generate_predictions()
