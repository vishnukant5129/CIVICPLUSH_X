"""
CivicPulse AI — Google OAuth 2.0 Service.

Implements a secure Authorization Code flow:

    1. Backend generates a random `state` token and stores it in Redis.
    2. Frontend redirects user to Google with this `state`.
    3. Google redirects back to backend callback with `code` + `state`.
    4. Backend validates `state` (CSRF protection), then exchanges `code`
       for tokens via Google's token endpoint.
    5. Backend verifies the returned ID token (signature, audience, issuer,
       expiry, subject).
    6. Verified identity is used to find/create a CivicPulse user.
    7. CivicPulse Redis session is created.
    8. HttpOnly session cookie is set and user is redirected to frontend.

SECURITY:
    - GOOGLE_CLIENT_SECRET never leaves the backend.
    - Google access/refresh tokens are NOT stored in MongoDB or cookies.
    - ID token verification is performed using Google's public certs
      via google-auth library (signature + audience + issuer + expiry).
    - `state` is a 32-byte cryptographically random token with a 10-minute TTL.
    - `sub` (Google subject identifier) is the stable, immutable identity key.
    - Email is verified (email_verified=True) before being trusted.
    - New public sign-ins are always assigned CITIZEN role.
    - No password is ever received, stored, or logged.
"""

from __future__ import annotations

import json
import logging
import secrets
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import httpx
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token

from app.config import get_settings
from app.database import redis

logger = logging.getLogger("civicpulse.google_oauth")

# Google OAuth 2.0 endpoints
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_CERTS_URL = "https://www.googleapis.com/oauth2/v3/certs"
GOOGLE_REVOKE_URL = "https://oauth2.googleapis.com/revoke"

# Minimum required scopes
GOOGLE_SCOPES = "openid email profile"

# State token Redis prefix + TTL
_STATE_PREFIX = "oauth_state:"
_STATE_TTL_SECONDS = 600  # 10 minutes


class GoogleOAuthError(Exception):
    """Raised when Google OAuth flow fails for a known, safe reason."""


class GoogleOAuthService:
    """Handles Google OAuth 2.0 Authorization Code flow."""

    # -----------------------------------------------------------------
    # Step 1: Generate state + build authorization URL
    # -----------------------------------------------------------------

    @staticmethod
    async def create_authorization_url() -> str:
        """
        Generate a CSRF state token, persist it in Redis, and build
        the Google authorization URL.

        Returns:
            The full Google authorization URL to redirect the user to.
        """
        settings = get_settings()

        if not settings.google_client_id:
            raise GoogleOAuthError(
                "GOOGLE_CLIENT_ID is not configured. "
                "Add it to your .env file before using Google Sign-In."
            )

        # Cryptographically random state for CSRF protection
        state = secrets.token_urlsafe(32)

        # Store state in Redis with a 10-minute TTL
        client = redis.get_client()
        if client is None:
            raise GoogleOAuthError("Redis unavailable — cannot create OAuth state.")
        await client.setex(f"{_STATE_PREFIX}{state}", _STATE_TTL_SECONDS, "1")

        params = {
            "client_id": settings.google_client_id,
            "redirect_uri": settings.google_redirect_uri,
            "response_type": "code",
            "scope": GOOGLE_SCOPES,
            "state": state,
            "access_type": "online",  # No refresh token needed for auth-only
            "prompt": "select_account",  # Always show account picker
        }

        return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"

    # -----------------------------------------------------------------
    # Step 2: Validate state (CSRF check)
    # -----------------------------------------------------------------

    @staticmethod
    async def validate_state(state: str) -> None:
        """
        Validate the OAuth state token against Redis.
        Deletes the token after validation (single-use).

        Raises:
            GoogleOAuthError: If state is missing, expired, or invalid.
        """
        if not state:
            raise GoogleOAuthError("Missing OAuth state parameter.")

        client = redis.get_client()
        if client is None:
            raise GoogleOAuthError("Redis unavailable — cannot validate OAuth state.")

        key = f"{_STATE_PREFIX}{state}"
        stored = await client.get(key)
        if not stored:
            raise GoogleOAuthError(
                "Invalid or expired OAuth state. Please start the sign-in again."
            )

        # Single-use: delete immediately after validation
        await client.delete(key)

    # -----------------------------------------------------------------
    # Step 3: Exchange authorization code for tokens
    # -----------------------------------------------------------------

    @staticmethod
    async def exchange_code(code: str) -> Dict[str, Any]:
        """
        Exchange the authorization code for Google tokens.

        Returns the raw token response dict which includes id_token.
        The access_token and refresh_token are NOT stored anywhere.

        Raises:
            GoogleOAuthError: If the exchange fails.
        """
        settings = get_settings()

        if not settings.google_client_secret:
            raise GoogleOAuthError(
                "GOOGLE_CLIENT_SECRET is not configured. "
                "Add it to your .env file."
            )

        payload = {
            "code": code,
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "redirect_uri": settings.google_redirect_uri,
            "grant_type": "authorization_code",
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(GOOGLE_TOKEN_URL, data=payload)

        if response.status_code != 200:
            logger.error(
                "Google token exchange failed: status=%d", response.status_code
            )
            raise GoogleOAuthError("Google token exchange failed. Please try again.")

        token_data = response.json()

        if "id_token" not in token_data:
            raise GoogleOAuthError("Google did not return an ID token.")

        return token_data

    # -----------------------------------------------------------------
    # Step 4: Verify ID token and extract verified identity
    # -----------------------------------------------------------------

    @staticmethod
    def verify_id_token(id_token_str: str) -> Dict[str, Any]:
        """
        Verify the Google ID token using google-auth library.

        Validates:
            - Cryptographic signature (via Google's public certs)
            - Issuer (accounts.google.com / https://accounts.google.com)
            - Audience (must match GOOGLE_CLIENT_ID)
            - Expiration (token must not be expired)
            - Subject (must be present and non-empty)
            - email_verified (must be True)

        Returns:
            Dict with verified claims: sub, email, name, picture.

        Raises:
            GoogleOAuthError: If any verification step fails.
        """
        settings = get_settings()

        if not settings.google_client_id:
            raise GoogleOAuthError("GOOGLE_CLIENT_ID is not configured.")

        try:
            # google-auth performs full cryptographic + claim verification
            idinfo = google_id_token.verify_oauth2_token(
                id_token_str,
                google_requests.Request(),
                settings.google_client_id,
            )
        except ValueError as exc:
            logger.warning("Google ID token verification failed: %s", str(exc))
            raise GoogleOAuthError("Google identity could not be verified. Please try again.")

        # Verify email is confirmed by Google
        if not idinfo.get("email_verified"):
            raise GoogleOAuthError(
                "Your Google account email is not verified. "
                "Please verify your Google account email first."
            )

        sub = idinfo.get("sub", "").strip()
        if not sub:
            raise GoogleOAuthError("Google identity is missing the subject identifier.")

        email = idinfo.get("email", "").strip().lower()
        if not email or "@" not in email:
            raise GoogleOAuthError("Google identity is missing a valid email address.")

        return {
            "sub": sub,
            "email": email,
            "full_name": idinfo.get("name", "").strip() or email.split("@")[0],
            "picture": idinfo.get("picture", None),
        }
