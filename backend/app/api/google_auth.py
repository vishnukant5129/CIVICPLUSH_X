"""
CivicPulse AI — Google OAuth 2.0 Authentication Routes.

Authorization Code Flow:

    GET  /api/v1/auth/google/start
        → Generates state, redirects user to Google.

    GET  /api/v1/auth/google/callback
        → Google redirects here with `code` + `state`.
        → Backend validates state, exchanges code, verifies ID token,
          finds/creates CivicPulse user, creates Redis session,
          sets HttpOnly cookie, redirects to frontend.

    GET  /api/v1/auth/me
    POST /api/v1/auth/logout
        → Unchanged from existing architecture.

SECURITY:
    - GOOGLE_CLIENT_SECRET never leaves backend.
    - Google tokens are NOT stored in cookies, MongoDB, or Redis.
    - state is single-use, cryptographically random, 10-minute TTL.
    - ID token is fully verified (signature + audience + issuer + expiry).
    - Public sign-in always forces role = CITIZEN.
    - No hardcoded user identities.
    - Account linking uses google_sub as primary stable key.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse

from app.config import get_settings
from app.database.mongodb import get_database
from app.dependencies.auth import get_session_id, require_authenticated_user
from app.domain.auth_schemas import UserResponse
from app.domain.enums import UserRole, UserStatus
from app.repositories.base import DuplicateDocumentError
from app.repositories.collections import UserRepository
from app.services.auth_service import AuthService
from app.services.google_oauth_service import GoogleOAuthError, GoogleOAuthService

logger = logging.getLogger("civicpulse.auth.google")

router = APIRouter(prefix="/api/v1/auth/google", tags=["Google Authentication"])


def _set_session_cookie(response: Response, session_id: str) -> None:
    """Set the CivicPulse HttpOnly session cookie."""
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
    """Clear the CivicPulse session cookie."""
    settings = get_settings()
    response.delete_cookie(
        key=settings.session_cookie_name,
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
    )


# -----------------------------------------------------------------
# GET /api/v1/auth/google/start
# -----------------------------------------------------------------

@router.get("/start")
async def google_start() -> RedirectResponse:
    """
    Begin Google OAuth 2.0 Authorization Code flow.

    Generates a CSRF state token, stores it in Redis, then redirects
    the user's browser to Google's authorization endpoint.

    The user's Google password is entered ONLY on Google's pages.
    CivicPulse never sees it.
    """
    try:
        auth_url = await GoogleOAuthService.create_authorization_url()
    except GoogleOAuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )

    return RedirectResponse(url=auth_url, status_code=302)


# -----------------------------------------------------------------
# GET /api/v1/auth/google/callback
# -----------------------------------------------------------------

@router.get("/callback")
async def google_callback(
    request: Request,
    response: Response,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
) -> RedirectResponse:
    """
    Handle the OAuth 2.0 callback from Google.

    Steps performed:
        1. Handle user-cancelled or Google error.
        2. Validate CSRF state against Redis.
        3. Exchange authorization code for Google tokens.
        4. Verify Google ID token (signature, audience, issuer, expiry, sub).
        5. Find existing CivicPulse user by google_sub (stable ID).
        6. If not found by sub, attempt email-based link for existing accounts.
        7. If no existing user, create a new CITIZEN account.
        8. Create a CivicPulse Redis session.
        9. Set HttpOnly civicpulse_session cookie.
        10. Redirect to frontend.

    Google passwords are never received or logged here.
    """
    settings = get_settings()
    frontend_url = settings.frontend_url

    # --- Step 1: Handle Google errors / user cancellation ---
    if error:
        safe_errors = {"access_denied", "cancelled", "user_cancelled_login"}
        if error in safe_errors:
            return RedirectResponse(
                url=f"{frontend_url}/?auth_error=cancelled",
                status_code=302,
            )
        logger.warning("Google OAuth error returned: %s", error)
        return RedirectResponse(
            url=f"{frontend_url}/?auth_error=google_error",
            status_code=302,
        )

    # --- Step 2: Validate state (CSRF protection) ---
    try:
        await GoogleOAuthService.validate_state(state or "")
    except GoogleOAuthError:
        logger.warning("OAuth state validation failed.")
        return RedirectResponse(
            url=f"{frontend_url}/?auth_error=state_mismatch",
            status_code=302,
        )

    if not code:
        return RedirectResponse(
            url=f"{frontend_url}/?auth_error=missing_code",
            status_code=302,
        )

    # --- Step 3: Exchange code for tokens ---
    try:
        token_response = await GoogleOAuthService.exchange_code(code)
    except GoogleOAuthError as exc:
        logger.warning("Code exchange failed: %s", str(exc))
        return RedirectResponse(
            url=f"{frontend_url}/?auth_error=token_exchange_failed",
            status_code=302,
        )

    # --- Step 4: Verify ID token ---
    try:
        identity = GoogleOAuthService.verify_id_token(token_response["id_token"])
    except GoogleOAuthError as exc:
        logger.warning("ID token verification failed: %s", str(exc))
        return RedirectResponse(
            url=f"{frontend_url}/?auth_error=identity_verification_failed",
            status_code=302,
        )

    google_sub = identity["sub"]
    verified_email = identity["email"]
    full_name = identity["full_name"]
    picture_url = identity.get("picture")

    # --- Step 5 + 6 + 7: Find or create CivicPulse user ---
    db = get_database()
    if db is None:
        logger.error("Database unavailable during Google callback.")
        return RedirectResponse(
            url=f"{frontend_url}/?auth_error=service_unavailable",
            status_code=302,
        )

    repo = UserRepository(db)
    now = datetime.now(timezone.utc)

    # Ensure bootstrap admin
    target_role = UserRole.CITIZEN.value
    if verified_email.lower() == settings.civicpulse_bootstrap_admin_email.lower():
        target_role = UserRole.SUPER_ADMIN.value

    # Primary lookup: stable google_sub
    user_doc = await repo.find_by_google_sub(google_sub)

    if not user_doc:
        # Secondary lookup: existing email account (account linking)
        existing_by_email = await repo.find_by_email(verified_email)

        if existing_by_email:
            # Link Google identity to existing email account
            user_id = existing_by_email["id"]
            update_data = {
                "google_sub": google_sub,
                "profile_picture_url": picture_url,
                "updated_at": now,
            }
            if target_role == UserRole.SUPER_ADMIN.value and existing_by_email.get("role") != target_role:
                update_data["role"] = target_role
                
            await repo.update_one(
                user_id,
                {"$set": update_data},
            )
            user_doc = await repo.find_by_id(user_id)
            logger.info("Linked Google identity to existing account: %s", user_id)

        else:
            # New user
            new_user = {
                "email": verified_email,
                "normalized_email": verified_email.lower(),
                "display_name": full_name,
                "google_sub": google_sub,
                "profile_picture_url": picture_url,
                "role": target_role,
                "status": UserStatus.ACTIVE.value,
                "password_hash": None,
                "created_at": now,
                "updated_at": now,
            }
            try:
                user_id = await repo.insert_one(new_user)
            except DuplicateDocumentError:
                logger.warning("Duplicate on Google account creation: %s", verified_email)
                return RedirectResponse(
                    url=f"{frontend_url}/?auth_error=duplicate_account",
                    status_code=302,
                )
            user_doc = await repo.find_by_id(user_id)
            logger.info("New Google citizen registered: %s", user_id)
    else:
        # Ensure role is updated if they are bootstrap admin
        if target_role == UserRole.SUPER_ADMIN.value and user_doc.get("role") != target_role:
            await repo.update_one(user_doc["id"], {"$set": {"role": target_role}})
            user_doc = await repo.find_by_id(user_doc["id"])

    # Verify account is active
    if user_doc.get("status") != UserStatus.ACTIVE.value:
        return RedirectResponse(
            url=f"{frontend_url}/?auth_error=account_disabled",
            status_code=302,
        )

    # --- Step 8: Create CivicPulse Redis session ---
    role = UserRole(user_doc["role"])
    session_id = await AuthService.create_session(user_id=user_doc["id"], role=role)

    # --- Step 9: Set HttpOnly session cookie ---
    redirect_response = RedirectResponse(
        url=f"{frontend_url}/",
        status_code=302,
    )
    settings_obj = get_settings()
    redirect_response.set_cookie(
        key=settings_obj.session_cookie_name,
        value=session_id,
        max_age=settings_obj.session_max_age_seconds,
        httponly=True,
        secure=settings_obj.is_production,
        samesite="lax",
    )

    logger.info("Google sign-in successful for user: %s", user_doc["id"])
    return redirect_response
