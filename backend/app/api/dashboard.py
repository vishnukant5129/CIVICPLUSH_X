"""
CivicPulse AI — Dashboard API Routes.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.database.mongodb import get_database
from app.dependencies.auth import RoleChecker
from app.domain.auth_schemas import UserResponse
from app.domain.enums import UserRole
from app.domain.dashboard_schemas import DashboardSummaryResponse, GeoJSONFeatureCollection
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard"])
citizen_only = RoleChecker([UserRole.CITIZEN])

def get_dashboard_service() -> DashboardService:
    db = get_database()
    if db is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    return DashboardService(db)

@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(
    status: Optional[str] = Query(None, description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    date_from: Optional[str] = Query(None, description="Filter from date (ISO)"),
    date_to: Optional[str] = Query(None, description="Filter to date (ISO)"),
    current_user: UserResponse = Depends(citizen_only),
    dashboard_service: DashboardService = Depends(get_dashboard_service),
) -> DashboardSummaryResponse:
    """Retrieve aggregate statistics for the dashboard, scoped to the user."""
    return await dashboard_service.get_summary(
        user_id=current_user.id,
        status=status,
        category=category,
        date_from=date_from,
        date_to=date_to
    )

@router.get("/complaints/map", response_model=GeoJSONFeatureCollection)
async def get_dashboard_map(
    status: Optional[str] = Query(None, description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    date_from: Optional[str] = Query(None, description="Filter from date (ISO)"),
    date_to: Optional[str] = Query(None, description="Filter to date (ISO)"),
    current_user: UserResponse = Depends(citizen_only),
    dashboard_service: DashboardService = Depends(get_dashboard_service),
) -> GeoJSONFeatureCollection:
    """Retrieve GeoJSON map data for the dashboard, scoped to the user."""
    return await dashboard_service.get_map_data(
        user_id=current_user.id,
        status=status,
        category=category,
        date_from=date_from,
        date_to=date_to
    )
