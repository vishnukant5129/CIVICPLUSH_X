"""
CivicPulse AI — Authority Tests.
"""

from unittest.mock import AsyncMock, patch
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import create_app
from app.domain.enums import ComplaintStatus

@pytest.fixture
def app():
    return create_app()

@pytest.fixture
async def client_authority(app):
    with patch("app.dependencies.auth.AuthService.get_session", return_value={"user_id": "auth_user_1", "role": "authority"}):
        with patch("app.dependencies.auth.UserRepository") as mock_user_repo_class:
            mock_user_repo = AsyncMock()
            mock_user_repo.find_by_id.return_value = {"id": "auth_user_1", "role": "authority", "status": "active", "email": "auth@example.com", "display_name": "Auth"}
            mock_user_repo_class.return_value = mock_user_repo
            
            with patch("app.api.authority.get_database", return_value=AsyncMock()):
                with patch("app.dependencies.auth.get_database", return_value=AsyncMock()):
                    transport = ASGITransport(app=app)
                    async with AsyncClient(transport=transport, base_url="http://test") as ac:
                        ac.cookies.set("civicpulse_session", "fake_session_auth")
                        yield ac

@pytest.fixture
async def client_citizen(app):
    with patch("app.dependencies.auth.AuthService.get_session", return_value={"user_id": "cit_1", "role": "citizen"}):
        with patch("app.dependencies.auth.UserRepository") as mock_user_repo_class:
            mock_user_repo = AsyncMock()
            mock_user_repo.find_by_id.return_value = {"id": "cit_1", "role": "citizen", "status": "active", "email": "cit@example.com", "display_name": "Cit"}
            mock_user_repo_class.return_value = mock_user_repo
            
            with patch("app.api.authority.get_database", return_value=AsyncMock()):
                with patch("app.dependencies.auth.get_database", return_value=AsyncMock()):
                    transport = ASGITransport(app=app)
                    async with AsyncClient(transport=transport, base_url="http://test") as ac:
                        ac.cookies.set("civicpulse_session", "fake_session_cit")
                        yield ac

@pytest.mark.asyncio
class TestAuthorityAPI:

    @patch("app.api.authority.AuthorityService")
    async def test_assign_complaint_success(self, mock_auth_service_class, client_authority):
        mock_auth_service = AsyncMock()
        mock_auth_service.assign_complaint.return_value = True
        mock_auth_service_class.return_value = mock_auth_service
        
        response = await client_authority.post(
            "/api/v1/authority/complaints/comp_1/assign",
            json={"department_id": "dept_1", "authority_id": "auth_user_1"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "success"

    @patch("app.api.authority.AuthorityService")
    async def test_update_status_success(self, mock_auth_service_class, client_authority):
        mock_auth_service = AsyncMock()
        mock_auth_service.update_status.return_value = True
        mock_auth_service_class.return_value = mock_auth_service
        
        response = await client_authority.post(
            "/api/v1/authority/complaints/comp_1/status",
            json={"new_status": ComplaintStatus.IN_PROGRESS.value, "note": "Working on it"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "success"

    async def test_citizen_forbidden(self, client_citizen):
        response = await client_citizen.post(
            "/api/v1/authority/complaints/comp_1/assign",
            json={"department_id": "dept_1", "authority_id": "auth_user_1"}
        )
        assert response.status_code == 403

    @patch("app.api.authority.GovernmentIntegrationAdapter")
    async def test_external_delivery_not_configured(self, mock_adapter_class, client_authority):
        mock_adapter = AsyncMock()
        mock_adapter.deliver_complaint.return_value = {
            "status": "not_configured",
            "provider": "unavailable_external_provider",
            "error_reason": "No external government API integration is configured.",
            "complaint_id": "comp_1",
            "integration_id": "mock-integration",
            "request_timestamp": "2026-08-16T10:00:00Z"
        }
        mock_adapter.db = AsyncMock()
        mock_adapter.db["complaints"].find_one = AsyncMock(return_value={"_id": "comp_1"})
        mock_adapter_class.return_value = mock_adapter

        response = await client_authority.post("/api/v1/authority/complaints/comp_1/external-delivery")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "not_configured"
        assert data["error_reason"] == "No external government API integration is configured."
