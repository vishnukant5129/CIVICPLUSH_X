"""
CivicPulse AI — Phase 11 Authority & Admin Operations Dashboard Test Suite.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch
import pytest
from httpx import ASGITransport, AsyncClient

from app.dependencies.auth import require_authenticated_user
from app.domain.auth_schemas import UserResponse
from app.domain.enums import UserRole, ComplaintStatus, CivicCategory
from app.main import app

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def citizen_client():
    mock_user = UserResponse(
        id="citizen_user_303",
        email="citizen@example.com",
        display_name="John Citizen",
        role=UserRole.CITIZEN,
    )
    app.dependency_overrides[require_authenticated_user] = lambda: mock_user
    with patch("app.api.authority.get_database", return_value=AsyncMock()):
        with patch("app.dependencies.auth.get_database", return_value=AsyncMock()):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def authority_client():
    mock_user = UserResponse(
        id="auth_user_101",
        email="officer@city.gov",
        display_name="Officer Jane Doe",
        role=UserRole.AUTHORITY,
        department_id="dept_road",
    )
    app.dependency_overrides[require_authenticated_user] = lambda: mock_user
    with patch("app.api.authority.get_database", return_value=AsyncMock()):
        with patch("app.dependencies.auth.get_database", return_value=AsyncMock()):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def admin_client():
    mock_user = UserResponse(
        id="admin_user_202",
        email="admin@city.gov",
        display_name="Admin Director",
        role=UserRole.ADMIN,
    )
    app.dependency_overrides[require_authenticated_user] = lambda: mock_user
    with patch("app.api.authority.get_database", return_value=AsyncMock()):
        with patch("app.dependencies.auth.get_database", return_value=AsyncMock()):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                yield ac
    app.dependency_overrides.clear()


@pytest.mark.asyncio
class TestAuthorityDashboardAPI:
    async def test_citizen_access_denied(self, citizen_client):
        """Citizens cannot access authority summary or queue endpoints."""
        res_summary = await citizen_client.get("/api/v1/authority/dashboard/summary")
        assert res_summary.status_code == 403

        res_queue = await citizen_client.get("/api/v1/authority/complaints")
        assert res_queue.status_code == 403

    async def test_authority_dashboard_summary(self, authority_client):
        """Authority user can retrieve aggregated summary statistics."""
        mock_summary = {
            "total_complaints": 12,
            "unassigned_count": 4,
            "assigned_to_me_count": 3,
            "in_progress_count": 5,
            "resolved_count": 2,
            "closed_count": 1,
            "status_counts": [{"status": "submitted", "count": 4}, {"status": "in_progress", "count": 5}],
            "category_counts": [{"category": "pothole_road_damage", "count": 8}],
            "recent_audit_activity": [],
            "integration_status": {"not_configured": 12},
            "scope_note": "Department operational scope (dept_road)",
        }

        with patch("app.api.authority.AuthorityService.get_authority_dashboard_summary", return_value=mock_summary):
            res = await authority_client.get("/api/v1/authority/dashboard/summary")
            assert res.status_code == 200
            data = res.json()
            assert data["total_complaints"] == 12
            assert data["in_progress_count"] == 5
            assert "dept_road" in data["scope_note"]

    async def test_authority_complaint_queue_filtering_and_pagination(self, authority_client):
        """Authority user can retrieve paginated complaint queue."""
        mock_queue = {
            "items": [
                {
                    "_id": "comp_101",
                    "title": "Severe Pothole",
                    "description": "Damage on Main St",
                    "category": "pothole_road_damage",
                    "status": "submitted",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "user_id": "citizen_user_1",
                    "evidence_count": 1,
                }
            ],
            "total": 1,
            "page": 1,
            "page_size": 20,
            "total_pages": 1,
        }

        with patch("app.api.authority.AuthorityService.get_authority_complaint_queue", return_value=mock_queue):
            res = await authority_client.get("/api/v1/authority/complaints?status=submitted&page=1&page_size=20")
            assert res.status_code == 200
            data = res.json()
            assert data["total"] == 1
            assert data["items"][0]["_id"] == "comp_101"

    async def test_authority_complaint_detail(self, authority_client):
        """Authority user can retrieve enriched complaint detail."""
        mock_detail = {
            "complaint": {
                "_id": "comp_101",
                "title": "Severe Pothole",
                "description": "Damage on Main St",
                "category": "pothole_road_damage",
                "status": "assigned",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "user_id": "citizen_user_1",
            },
            "evidence": [],
            "ai_analysis": [],
            "assignment": {"department_id": "dept_road", "assigned_authority_id": "auth_user_101"},
            "status_history": [],
            "audit_trail": [],
            "routing_info": {"matched": True, "department_id": "dept_road"},
            "intelligence": None,
            "external_delivery": None,
        }

        with patch("app.api.authority.AuthorityService.get_authority_complaint_detail", return_value=mock_detail):
            res = await authority_client.get("/api/v1/authority/complaints/comp_101")
            assert res.status_code == 200
            data = res.json()
            assert data["complaint"]["_id"] == "comp_101"
            assert data["assignment"]["department_id"] == "dept_road"

    async def test_evidence_download_forbidden_for_other_citizen(self, citizen_client):
        """Citizen cannot download evidence belonging to another citizen's complaint."""
        mock_ev = {
            "_id": "ev_101",
            "complaint_id": "comp_other_999",
            "user_id": "other_citizen_888",
            "storage_key": "comp_other_999/sample.jpg",
        }
        mock_comp = {
            "_id": "comp_other_999",
            "user_id": "other_citizen_888",
        }

        with patch("app.repositories.collections.EvidenceRepository.find_by_id", return_value=mock_ev):
            with patch("app.repositories.collections.ComplaintRepository.find_by_id", return_value=mock_comp):
                res = await citizen_client.get("/api/v1/authority/evidence/ev_101/download")
                assert res.status_code in [403, 404]
