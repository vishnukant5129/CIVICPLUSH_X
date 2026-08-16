"""
CivicPulse AI — Authentication Dependencies.

FastAPI dependencies for resolving the current user, enforcing
authentication, and verifying roles.
"""

from __future__ import annotations

from typing import Optional

from fastapi import Cookie, Depends, HTTPException, Request, status

from app.config import get_settings
from app.database.mongodb import get_database
from app.domain.auth_schemas import UserResponse
from app.domain.enums import UserRole, UserStatus
from app.repositories.collections import UserRepository
from app.services.auth_service import AuthService


async def get_session_id(request: Request) -> Optional[str]:
    """Extract session ID from the cookie."""
    settings = get_settings()
    return request.cookies.get(settings.session_cookie_name)


async def get_current_user(
    session_id: Optional[str] = Depends(get_session_id),
) -> Optional[UserResponse]:
    """
    Resolve the current authenticated user from the session.
    Returns None if unauthenticated.
    """
    if not session_id:
        return None

    session_data = await AuthService.get_session(session_id)
    if not session_data:
        return None

    user_id = session_data.get("user_id")
    if not user_id:
        return None

    # Verify user still exists and is active
    db = get_database()
    if db is None:
        return None
        
    repo = UserRepository(db)
    user_doc = await repo.find_by_id(user_id)
    
    if not user_doc:
        return None
        
    if user_doc.get("status") != UserStatus.ACTIVE.value:
        return None

    return UserResponse(**user_doc)


async def require_authenticated_user(
    current_user: Optional[UserResponse] = Depends(get_current_user),
) -> UserResponse:
    """
    Dependency that enforces authentication.
    Raises 401 if unauthenticated.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Cookie"},
        )
    return current_user


class RoleChecker:
    """
    Dependency generator for role-based authorization.
    Usage:
        Depends(RoleChecker([UserRole.ADMIN, UserRole.AUTHORITY]))
    """

    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles

    async def __call__(
        self, current_user: UserResponse = Depends(require_authenticated_user)
    ) -> UserResponse:
        """Enforce role check."""
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to perform this operation.",
            )
        return current_user
