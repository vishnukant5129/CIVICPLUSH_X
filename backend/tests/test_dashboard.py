"""
CivicPulse AI — Dashboard Tests.
"""

from unittest.mock import AsyncMock, patch
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import create_app

@pytest.fixture
def app():
    return create_app()

@pytest.fixture
async def client_a(app):
    with patch("app.dependencies.auth.AuthService.get_session", return_value={"user_id": "user_a", "role": "citizen"}):
        with patch("app.dependencies.auth.UserRepository") as mock_user_repo_class:
            mock_user_repo = AsyncMock()
            mock_user_repo.find_by_id.return_value = {"id": "user_a", "role": "citizen", "status": "active", "email": "a@example.com", "display_name": "A"}
            mock_user_repo_class.return_value = mock_user_repo
            
            with patch("app.api.dashboard.get_database", return_value=AsyncMock()):
                with patch("app.dependencies.auth.get_database", return_value=AsyncMock()):
                    transport = ASGITransport(app=app)
                    async with AsyncClient(transport=transport, base_url="http://test") as ac:
                        ac.cookies.set("civicpulse_session", "fake_session_a")
                        yield ac

@pytest.mark.asyncio
class TestDashboard:

    @patch("app.api.dashboard.DashboardService")
    async def test_dashboard_summary_ownership(self, mock_dashboard_service_class, client_a):
        mock_dashboard_service = AsyncMock()
        mock_dashboard_service.get_summary.return_value = {
            "total_complaints": 5,
            "status_counts": [{"status": "submitted", "count": 5}],
            "category_counts": [{"category": "other", "count": 5}],
            "trend": [{"date": "2026-08-16", "count": 5}],
            "complaints_with_evidence": 2,
            "ai_stats": {"completed": 1, "processing": 1, "failed": 0}
        }
        mock_dashboard_service_class.return_value = mock_dashboard_service

        response = await client_a.get("/api/v1/dashboard/summary")
        assert response.status_code == 200
        data = response.json()
        assert data["total_complaints"] == 5
        
        # Verify that get_summary was called with user_a
        mock_dashboard_service.get_summary.assert_called_once()
        kwargs = mock_dashboard_service.get_summary.call_args.kwargs
        assert kwargs["user_id"] == "user_a"

    @patch("app.api.dashboard.DashboardService")
    async def test_dashboard_map_ownership(self, mock_dashboard_service_class, client_a):
        mock_dashboard_service = AsyncMock()
        mock_dashboard_service.get_map_data.return_value = {
            "type": "FeatureCollection",
            "features": []
        }
        mock_dashboard_service_class.return_value = mock_dashboard_service

        response = await client_a.get("/api/v1/dashboard/complaints/map")
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "FeatureCollection"
        
        # Verify that get_map_data was called with user_a
        mock_dashboard_service.get_map_data.assert_called_once()
        kwargs = mock_dashboard_service.get_map_data.call_args.kwargs
        assert kwargs["user_id"] == "user_a"
