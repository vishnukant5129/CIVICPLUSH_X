"""
CivicPulse AI — Notifications API.

Router providing endpoints for user notification inbox, read/unread management,
and notification channel preferences.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from app.database.mongodb import get_database
from app.dependencies.auth import require_authenticated_user
from app.domain.auth_schemas import UserResponse
from app.domain.notification_schemas import (
    NotificationPreferences,
    NotificationResponse,
)
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/api/v1/notifications", tags=["Notifications"])


def get_notification_service() -> NotificationService:
    db = get_database()
    return NotificationService(db)


class UpdatePreferencesRequest(BaseModel):
    in_app_enabled: Optional[bool] = None
    email_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None


@router.get("", response_model=List[NotificationResponse])
async def get_my_notifications(
    unread_only: bool = Query(False, description="Filter to only unread notifications"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: UserResponse = Depends(require_authenticated_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Retrieve notifications for the authenticated user."""
    return await service.get_user_notifications(
        user_id=current_user.id,
        unread_only=unread_only,
        skip=skip,
        limit=limit,
    )


@router.get("/unread-count")
async def get_my_unread_count(
    current_user: UserResponse = Depends(require_authenticated_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Get total unread notifications count for the authenticated user."""
    count = await service.get_unread_count(user_id=current_user.id)
    return {"unread_count": count}


@router.patch("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: UserResponse = Depends(require_authenticated_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Mark a specific notification as read."""
    success = await service.mark_as_read(notification_id=notification_id, user_id=current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found or access denied.",
        )
    return {"status": "success", "message": "Notification marked as read."}


@router.post("/mark-all-read")
async def mark_all_notifications_read(
    current_user: UserResponse = Depends(require_authenticated_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Mark all notifications for the authenticated user as read."""
    count = await service.mark_all_as_read(user_id=current_user.id)
    return {"status": "success", "marked_count": count}


@router.get("/preferences", response_model=NotificationPreferences)
async def get_my_preferences(
    current_user: UserResponse = Depends(require_authenticated_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Retrieve notification delivery channel preferences for the authenticated user."""
    return await service.get_user_preferences(user_id=current_user.id)


@router.put("/preferences", response_model=NotificationPreferences)
async def update_my_preferences(
    payload: UpdatePreferencesRequest,
    current_user: UserResponse = Depends(require_authenticated_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Update notification delivery channel preferences for the authenticated user."""
    update_dict = payload.model_dump(exclude_unset=True)
    return await service.update_user_preferences(
        user_id=current_user.id,
        preferences_update=update_dict,
    )
