"""
CivicPulse AI — Auth Tests.

Tests for registration, login, logout, and protected routes.
Uses mocked database and redis.
"""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

from app.domain.enums import UserRole, UserStatus
from app.main import create_app
from app.services.auth_service import AuthService
from app.config import Settings


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_db_repo():
    with patch("app.api.auth.UserRepository") as mock_repo_class:
        mock_repo = AsyncMock()
        mock_repo_class.return_value = mock_repo
        # Also patch get_database so it doesn't return None
        with patch("app.api.auth.get_database", return_value=AsyncMock()):
            yield mock_repo


@pytest.fixture
def mock_redis():
    with patch("app.services.auth_service.redis") as mock_redis_mod:
        mock_client = AsyncMock()
        mock_redis_mod.get_client.return_value = mock_client
        yield mock_client


@pytest.mark.asyncio
class TestRegistration:

    async def test_successful_registration(self, client, mock_db_repo, mock_redis):
        # Setup mock db
        mock_db_repo.insert_one.return_value = "507f1f77bcf86cd799439011"
        mock_db_repo.find_by_id.return_value = {
            "id": "507f1f77bcf86cd799439011",
            "email": "test@example.com",
            "display_name": "Test User",
            "role": UserRole.CITIZEN.value,
        }

        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "display_name": "Test User",
                "password": "StrongPassword123!"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["role"] == "citizen"
        assert "password" not in data
        assert "password_hash" not in data
        
        # Verify session cookie was set
        assert "civicpulse_session" in response.cookies

    async def test_duplicate_registration_returns_409(self, client, mock_db_repo):
        from app.repositories.base import DuplicateDocumentError
        mock_db_repo.insert_one.side_effect = DuplicateDocumentError()

        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "duplicate@example.com",
                "display_name": "Test User",
                "password": "StrongPassword123!"
            }
        )

        assert response.status_code == 409


@pytest.mark.asyncio
class TestLogin:

    async def test_successful_login(self, client, mock_db_repo, mock_redis):
        password_hash = AuthService.hash_password("correct_password")
        mock_db_repo.find_by_email.return_value = {
            "id": "user123",
            "email": "user@example.com",
            "display_name": "Test User",
            "role": UserRole.CITIZEN.value,
            "status": UserStatus.ACTIVE.value,
            "password_hash": password_hash,
        }

        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "correct_password"}
        )

        assert response.status_code == 200
        assert "civicpulse_session" in response.cookies

    async def test_invalid_password(self, client, mock_db_repo):
        password_hash = AuthService.hash_password("correct_password")
        mock_db_repo.find_by_email.return_value = {
            "id": "user123",
            "email": "user@example.com",
            "status": UserStatus.ACTIVE.value,
            "password_hash": password_hash,
        }

        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "wrong_password"}
        )

        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]


@pytest.mark.asyncio
class TestMeAndLogout:
    
    async def test_me_unauthenticated(self, client):
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401

    async def test_logout_clears_cookie(self, client, mock_redis):
        response = await client.post("/api/v1/auth/logout")
        assert response.status_code == 204
        # Cookie should be expired
        cookie = next((c for c in response.headers.get_list("set-cookie") if "civicpulse_session" in c), None)
        assert cookie is not None
        assert "Max-Age=0" in cookie or "expires=" in cookie.lower()
