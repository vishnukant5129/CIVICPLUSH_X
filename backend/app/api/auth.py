"""
CivicPulse AI — Authentication API Routes.

Handles registration, login, logout, and identity endpoints.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.config import get_settings
from app.database.mongodb import get_database
from app.dependencies.auth import get_session_id, require_authenticated_user
from app.domain.auth_schemas import LoginRequest, RegisterRequest, UserResponse
from app.domain.enums import UserRole, UserStatus
from app.repositories.base import DuplicateDocumentError
from app.repositories.collections import UserRepository
from app.services.auth_service import AuthService

logger = logging.getLogger("civicpulse.auth")

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


def _set_session_cookie(response: Response, session_id: str) -> None:
    """Helper to set secure session cookie."""
    settings = get_settings()
    response.set_cookie(
        key=settings.session_cookie_name,
        value=session_id,
        max_age=settings.session_max_age_seconds,
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
    )


def _clear_session_cookie(response: Response) -> None:
    """Helper to clear session cookie."""
    settings = get_settings()
    response.delete_cookie(
        key=settings.session_cookie_name,
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    response: Response,
) -> UserResponse:
    """
    Public registration for CITIZEN users.
    Cannot register admin or authority accounts.
    """
    db = get_database()
    if db is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    repo = UserRepository(db)
    
    # Enforce safe default role
    role = UserRole.CITIZEN
    
    # Hash password
    password_hash = AuthService.hash_password(request.password)
    
    user_doc = {
        "email": request.email,
        "normalized_email": request.email.lower(),
        "display_name": request.display_name,
        "role": role.value,
        "status": UserStatus.ACTIVE.value,
        "password_hash": password_hash,
    }
    
    try:
        user_id = await repo.insert_one(user_doc)
    except DuplicateDocumentError:
        # Standardize 409 Conflict for duplicates
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists."
        )
        
    # Auto-login after registration
    session_id = await AuthService.create_session(user_id, role)
    _set_session_cookie(response, session_id)
    
    logger.info("New citizen registered: %s", user_id)
    
    # Fetch full doc to ensure all defaults are present
    created_doc = await repo.find_by_id(user_id)
    return UserResponse(**created_doc)


@router.post("/login", response_model=UserResponse)
async def login(
    request: LoginRequest,
    response: Response,
) -> UserResponse:
    """
    Authenticate user and create session.
    Returns generic 401 on failure to prevent enumeration.
    """
    db = get_database()
    if db is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
        
    repo = UserRepository(db)
    
    # Generic error to prevent enumeration
    generic_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password.",
    )
    
    user_doc = await repo.find_by_email(request.email)
    if not user_doc:
        raise generic_error
        
    if not user_doc.get("password_hash"):
        raise generic_error
        
    if not AuthService.verify_password(request.password, user_doc["password_hash"]):
        raise generic_error
        
    if user_doc.get("status") != UserStatus.ACTIVE.value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is disabled or suspended.",
        )
        
    # Valid credentials
    session_id = await AuthService.create_session(
        user_id=user_doc["id"],
        role=UserRole(user_doc["role"]),
    )
    _set_session_cookie(response, session_id)
    
    logger.info("User logged in: %s", user_doc["id"])
    return UserResponse(**user_doc)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    session_id: str | None = Depends(get_session_id),
) -> None:
    """
    Destroy session and clear cookie.
    """
    if session_id:
        await AuthService.destroy_session(session_id)
    _clear_session_cookie(response)


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: UserResponse = Depends(require_authenticated_user),
) -> UserResponse:
    """
    Get current authenticated user identity.
    """
    return current_user
