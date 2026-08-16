"""
CivicPulse AI — Intelligence Tests.
"""

from unittest.mock import AsyncMock, patch
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import create_app
from app.domain.intelligence_schemas import RelationType

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
            
            with patch("app.api.intelligence.get_database", return_value=AsyncMock()):
                with patch("app.dependencies.auth.get_database", return_value=AsyncMock()):
                    transport = ASGITransport(app=app)
                    async with AsyncClient(transport=transport, base_url="http://test") as ac:
                        ac.cookies.set("civicpulse_session", "fake_session_a")
                        yield ac

@pytest.mark.asyncio
class TestIntelligence:

    @patch("app.api.intelligence.IntelligenceService")
    @patch("app.api.intelligence.ComplaintRepository")
    async def test_get_intelligence_success(self, mock_comp_repo_class, mock_intel_service_class, client_a):
        mock_comp_repo = AsyncMock()
        mock_comp_repo.find_by_id.return_value = {"id": "comp_1", "user_id": "user_a"}
        mock_comp_repo_class.return_value = mock_comp_repo
        
        mock_intel_service = AsyncMock()
        mock_intel_service.get_intelligence_for_complaint.return_value = {
            "complaint_id": "comp_1",
            "relations": [
                {
                    "id": "rel_1",
                    "complaint_a_id": "comp_1",
                    "complaint_b_id": "comp_2",
                    "relation_type": RelationType.DUPLICATE.value,
                    "semantic_similarity": 0.95,
                    "geographic_distance_meters": 50,
                    "category_match": True,
                    "temporal_distance_days": 1.5,
                    "match_score": 0.95,
                    "explanation": "High similarity",
                    "algorithm_version": "v1",
                    "created_at": "2026-08-16T10:00:00Z"
                }
            ],
            "cluster": {
                "id": "clust_1",
                "cluster_id": "CLUSTER-XYZ",
                "member_complaint_ids": ["comp_1", "comp_2"],
                "clustering_algorithm": "connected_components",
                "clustering_version": "v1",
                "created_at": "2026-08-16T10:00:00Z",
                "updated_at": "2026-08-16T10:00:00Z"
            }
        }
        mock_intel_service_class.return_value = mock_intel_service

        response = await client_a.get("/api/v1/intelligence/complaints/comp_1")
        assert response.status_code == 200
        data = response.json()
        assert data["complaint_id"] == "comp_1"
        assert len(data["relations"]) == 1
        assert data["relations"][0]["relation_type"] == "duplicate"
        assert data["cluster"]["cluster_id"] == "CLUSTER-XYZ"

    @patch("app.api.intelligence.ComplaintRepository")
    async def test_get_intelligence_forbidden(self, mock_comp_repo_class, client_a):
        mock_comp_repo = AsyncMock()
        mock_comp_repo.find_by_id.return_value = {"id": "comp_1", "user_id": "user_b"} # Belongs to B
        mock_comp_repo_class.return_value = mock_comp_repo
        
        response = await client_a.get("/api/v1/intelligence/complaints/comp_1")
        assert response.status_code == 403
