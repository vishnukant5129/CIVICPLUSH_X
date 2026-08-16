"""
CivicPulse AI — Complaint Tests.

Tests for complaint creation, fetching, ownership isolation.
"""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient, ASGITransport

from app.domain.enums import UserRole
from app.main import create_app

# Fake active citizen user
MOCK_USER_A = {
    "user_id": "user_a_123",
    "role": UserRole.CITIZEN.value,
    "status": "active"
}

MOCK_USER_B = {
    "user_id": "user_b_456",
    "role": UserRole.CITIZEN.value,
    "status": "active"
}


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
async def client_a(app):
    # Mock auth for User A
    with patch("app.dependencies.auth.AuthService.get_session", return_value={"user_id": "user_a_123", "role": "citizen"}):
        with patch("app.dependencies.auth.UserRepository") as mock_user_repo_class:
            mock_user_repo = AsyncMock()
            mock_user_repo.find_by_id.return_value = {"id": "user_a_123", "role": "citizen", "status": "active", "email": "a@example.com", "display_name": "A"}
            mock_user_repo_class.return_value = mock_user_repo
            
            with patch("app.api.complaints.get_database", return_value=AsyncMock()):
                with patch("app.dependencies.auth.get_database", return_value=AsyncMock()):
                    transport = ASGITransport(app=app)
                    async with AsyncClient(transport=transport, base_url="http://test") as ac:
                        ac.cookies.set("civicpulse_session", "fake_session_a")
                        yield ac


@pytest.fixture
def mock_complaint_service():
    with patch("app.api.complaints.ComplaintService") as mock_service_class:
        mock_service = AsyncMock()
        mock_service_class.return_value = mock_service
        yield mock_service


@pytest.mark.asyncio
class TestComplaintCreation:

    async def test_successful_complaint_creation(self, client_a, mock_complaint_service):
        # Mock service response
        mock_complaint_service.create_complaint.return_value = {
            "id": "comp_123",
            "user_id": "user_a_123",
            "title": "Pothole on Main St",
            "description": "Huge pothole causing traffic issues.",
            "category": "pothole_road_damage",
            "location": {"geo": {"type": "Point", "coordinates": [77.0, 28.0]}},
            "status": "submitted",
            "evidence_count": 0,
            "created_at": "2026-08-16T10:00:00Z",
            "updated_at": "2026-08-16T10:00:00Z"
        }

        payload = {
            "title": "Pothole on Main St",
            "description": "Huge pothole causing traffic issues.",
            "category": "pothole_road_damage",
            "location": {
                "geo": {"type": "Point", "coordinates": [77.0, 28.0]}
            }
        }
        
        response = await client_a.post("/api/v1/complaints/", json=payload)
        
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == "comp_123"
        assert data["status"] == "submitted"
        assert data["user_id"] == "user_a_123"
        
        # Verify service was called correctly
        mock_complaint_service.create_complaint.assert_called_once()
        args = mock_complaint_service.create_complaint.call_args[0]
        assert args[0] == "user_a_123"  # Server-derived user ID


@pytest.mark.asyncio
class TestComplaintOwnership:

    async def test_get_complaint_detail_ownership_enforced(self, client_a, mock_complaint_service):
        # Attempt to get a complaint
        mock_complaint_service.get_complaint_detail.return_value = None  # Service returns None if unauthorized/not found

        response = await client_a.get("/api/v1/complaints/comp_other")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Complaint not found."
        
        # Verify service was called with the authenticated user ID
        mock_complaint_service.get_complaint_detail.assert_called_once_with("comp_other", "user_a_123")

    async def test_list_my_complaints(self, client_a, mock_complaint_service):
        mock_complaint_service.get_user_complaints.return_value = [
            {
                "id": "comp_1",
                "user_id": "user_a_123",
                "title": "A",
                "description": "A"*10,
                "category": "other",
                "location": {"geo": {"type": "Point", "coordinates": [0, 0]}},
                "status": "submitted",
                "evidence_count": 0,
                "created_at": "2026-08-16T10:00:00Z",
                "updated_at": "2026-08-16T10:00:00Z"
            }
        ]

        response = await client_a.get("/api/v1/complaints/my")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["user_id"] == "user_a_123"
        
        mock_complaint_service.get_user_complaints.assert_called_once_with("user_a_123")
