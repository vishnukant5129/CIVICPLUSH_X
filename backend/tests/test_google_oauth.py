"""
CivicPulse AI — Google OAuth Service Unit Tests.

Tests the GoogleOAuthService in isolation using mocks for:
    - Redis (state storage)
    - httpx (Google token endpoint)
    - google-auth (ID token verification)

These tests do NOT call Google's real servers.
E2E verification with a real Google account must be done manually.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.google_oauth_service import GoogleOAuthError, GoogleOAuthService


# ============================================================
# create_authorization_url
# ============================================================

class TestCreateAuthorizationUrl:
    """Tests for state generation and URL building."""

    @pytest.mark.asyncio
    async def test_returns_google_auth_url(self):
        """Authorization URL must point to Google's endpoint."""
        mock_redis = AsyncMock()
        mock_redis.setex = AsyncMock()

        with (
            patch("app.services.google_oauth_service.redis.get_client", return_value=mock_redis),
            patch("app.services.google_oauth_service.get_settings") as mock_settings,
        ):
            settings = MagicMock()
            settings.google_client_id = "test-client-id.apps.googleusercontent.com"
            settings.google_redirect_uri = "http://localhost:8000/api/v1/auth/google/callback"
            mock_settings.return_value = settings

            url = await GoogleOAuthService.create_authorization_url()

        assert url.startswith("https://accounts.google.com/o/oauth2/v2/auth")
        assert "test-client-id.apps.googleusercontent.com" in url
        assert "openid" in url
        assert "email" in url
        assert "profile" in url
        assert "state=" in url

    @pytest.mark.asyncio
    async def test_raises_when_client_id_missing(self):
        """Must raise GoogleOAuthError when GOOGLE_CLIENT_ID is not set."""
        with patch("app.services.google_oauth_service.get_settings") as mock_settings:
            settings = MagicMock()
            settings.google_client_id = ""
            mock_settings.return_value = settings

            with pytest.raises(GoogleOAuthError, match="GOOGLE_CLIENT_ID"):
                await GoogleOAuthService.create_authorization_url()

    @pytest.mark.asyncio
    async def test_raises_when_redis_unavailable(self):
        """Must raise GoogleOAuthError when Redis is not available."""
        with (
            patch("app.services.google_oauth_service.redis.get_client", return_value=None),
            patch("app.services.google_oauth_service.get_settings") as mock_settings,
        ):
            settings = MagicMock()
            settings.google_client_id = "test-id"
            mock_settings.return_value = settings

            with pytest.raises(GoogleOAuthError, match="Redis"):
                await GoogleOAuthService.create_authorization_url()


# ============================================================
# validate_state
# ============================================================

class TestValidateState:
    """Tests for CSRF state validation."""

    @pytest.mark.asyncio
    async def test_valid_state_passes(self):
        """A state present in Redis should pass validation."""
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=b"1")
        mock_redis.delete = AsyncMock()

        with patch("app.services.google_oauth_service.redis.get_client", return_value=mock_redis):
            # Should not raise
            await GoogleOAuthService.validate_state("valid-state-token")

        mock_redis.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_invalid_state_raises(self):
        """An invalid/expired state must raise GoogleOAuthError."""
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=None)

        with patch("app.services.google_oauth_service.redis.get_client", return_value=mock_redis):
            with pytest.raises(GoogleOAuthError, match="Invalid or expired"):
                await GoogleOAuthService.validate_state("bad-state")

    @pytest.mark.asyncio
    async def test_empty_state_raises(self):
        """Empty state must raise GoogleOAuthError."""
        with pytest.raises(GoogleOAuthError, match="Missing"):
            await GoogleOAuthService.validate_state("")


# ============================================================
# verify_id_token
# ============================================================

class TestVerifyIdToken:
    """Tests for ID token verification."""

    def test_valid_token_returns_identity(self):
        """A valid, verified token must return clean identity dict."""
        mock_idinfo = {
            "sub": "1234567890",
            "email": "test@example.com",
            "email_verified": True,
            "name": "Test User",
            "picture": "https://lh3.googleusercontent.com/a/test",
        }

        with (
            patch("app.services.google_oauth_service.google_id_token.verify_oauth2_token", return_value=mock_idinfo),
            patch("app.services.google_oauth_service.get_settings") as mock_settings,
        ):
            settings = MagicMock()
            settings.google_client_id = "test-client-id"
            mock_settings.return_value = settings

            identity = GoogleOAuthService.verify_id_token("fake-id-token-str")

        assert identity["sub"] == "1234567890"
        assert identity["email"] == "test@example.com"
        assert identity["full_name"] == "Test User"
        assert "picture" in identity

    def test_unverified_email_raises(self):
        """A token where email_verified=False must be rejected."""
        mock_idinfo = {
            "sub": "1234567890",
            "email": "test@example.com",
            "email_verified": False,
            "name": "Test User",
        }

        with (
            patch("app.services.google_oauth_service.google_id_token.verify_oauth2_token", return_value=mock_idinfo),
            patch("app.services.google_oauth_service.get_settings") as mock_settings,
        ):
            settings = MagicMock()
            settings.google_client_id = "test-client-id"
            mock_settings.return_value = settings

            with pytest.raises(GoogleOAuthError, match="email is not verified"):
                GoogleOAuthService.verify_id_token("fake-token")

    def test_invalid_token_raises(self):
        """A cryptographically invalid token must raise GoogleOAuthError."""
        with (
            patch(
                "app.services.google_oauth_service.google_id_token.verify_oauth2_token",
                side_effect=ValueError("Token expired"),
            ),
            patch("app.services.google_oauth_service.get_settings") as mock_settings,
        ):
            settings = MagicMock()
            settings.google_client_id = "test-client-id"
            mock_settings.return_value = settings

            with pytest.raises(GoogleOAuthError, match="could not be verified"):
                GoogleOAuthService.verify_id_token("tampered-token")

    def test_missing_sub_raises(self):
        """A token missing the subject identifier must be rejected."""
        mock_idinfo = {
            "sub": "",
            "email": "test@example.com",
            "email_verified": True,
            "name": "Test User",
        }

        with (
            patch("app.services.google_oauth_service.google_id_token.verify_oauth2_token", return_value=mock_idinfo),
            patch("app.services.google_oauth_service.get_settings") as mock_settings,
        ):
            settings = MagicMock()
            settings.google_client_id = "test-client-id"
            mock_settings.return_value = settings

            with pytest.raises(GoogleOAuthError, match="subject identifier"):
                GoogleOAuthService.verify_id_token("fake-token")

    def test_missing_client_id_raises(self):
        """Must raise immediately if GOOGLE_CLIENT_ID is not configured."""
        with patch("app.services.google_oauth_service.get_settings") as mock_settings:
            settings = MagicMock()
            settings.google_client_id = ""
            mock_settings.return_value = settings

            with pytest.raises(GoogleOAuthError, match="GOOGLE_CLIENT_ID"):
                GoogleOAuthService.verify_id_token("fake-token")
