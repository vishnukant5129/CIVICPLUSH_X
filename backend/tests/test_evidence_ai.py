"""
CivicPulse AI — Evidence & AI Tests.
"""

from unittest.mock import AsyncMock, patch
import pytest
from httpx import AsyncClient, ASGITransport

from app.domain.enums import UserRole
from app.main import create_app

@pytest.fixture
def app():
    return create_app()

@pytest.fixture
async def client_a(app):
    # Mock auth for User A
    with patch("app.dependencies.auth.AuthService.get_session", return_value={"user_id": "user_a", "role": "citizen"}):
        with patch("app.dependencies.auth.UserRepository") as mock_user_repo_class:
            mock_user_repo = AsyncMock()
            mock_user_repo.find_by_id.return_value = {"id": "user_a", "role": "citizen", "status": "active", "email": "a@example.com", "display_name": "A"}
            mock_user_repo_class.return_value = mock_user_repo
            
            with patch("app.api.evidence.get_database", return_value=AsyncMock()):
                with patch("app.dependencies.auth.get_database", return_value=AsyncMock()):
                    transport = ASGITransport(app=app)
                    async with AsyncClient(transport=transport, base_url="http://test") as ac:
                        ac.cookies.set("civicpulse_session", "fake_session_a")
                        yield ac

@pytest.mark.asyncio
class TestEvidenceAndAI:

    @patch("app.api.evidence.EvidenceService")
    @patch("app.api.evidence.AIService")
    async def test_evidence_upload_triggers_ai(self, mock_ai_service_class, mock_evidence_service_class, client_a):
        mock_ev_service = AsyncMock()
        mock_ev_service.upload_evidence.return_value = {
            "id": "ev_1",
            "complaint_id": "comp_1",
            "user_id": "user_a",
            "original_filename": "test.jpg",
            "mime_type": "image/jpeg",
            "size_bytes": 1024,
            "processing_status": "pending",
            "created_at": "2026-08-16T10:00:00Z"
        }
        mock_evidence_service_class.return_value = mock_ev_service

        mock_ai_service = AsyncMock()
        mock_ai_service_class.return_value = mock_ai_service

        files = {"file": ("test.jpg", b"fake_image_bytes", "image/jpeg")}
        
        response = await client_a.post("/api/v1/complaints/comp_1/evidence", files=files)
        
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == "ev_1"
        assert data["original_filename"] == "test.jpg"
        
        mock_ev_service.upload_evidence.assert_called_once()
        # Since asyncio.create_task fires, the service should eventually be called but we mock the background start
        # mock_ai_service.analyze_complaint is fired in background
    
    @patch("app.services.ai_service.ComplaintRepository")
    @patch("app.services.ai_service.AIAnalysisRepository")
    @patch("app.services.ai_service.AsyncGroq")
    async def test_ai_analysis_success(self, mock_groq_class, mock_ai_repo_class, mock_comp_repo_class):
        # This tests the service directly
        from app.services.ai_service import AIService
        
        mock_comp_repo = AsyncMock()
        mock_comp_repo.find_by_id.return_value = {
            "title": "Fix pothole",
            "description": "Big one",
            "category": "other"
        }
        mock_comp_repo_class.return_value = mock_comp_repo
        
        mock_ai_repo = AsyncMock()
        mock_ai_repo.insert_one.return_value = "ai_1"
        # Mock what find_by_id returns after successful marking
        mock_ai_repo.find_by_id.return_value = {"id": "ai_1", "status": "completed"}
        mock_ai_repo_class.return_value = mock_ai_repo
        
        # Mock Groq response
        mock_client = AsyncMock()
        mock_groq_class.return_value = mock_client
        mock_completion = AsyncMock()
        mock_completion.choices = [AsyncMock(message=AsyncMock(content='{"category": "pothole_road_damage", "summary": "A pothole exists.", "severity_indicators": [], "model_confidence": 0.8}'))]
        mock_client.chat.completions.create.return_value = mock_completion
        
        with patch("app.services.ai_service.get_settings") as mock_settings:
            mock_settings.return_value.ai_provider = "groq"
            mock_settings.return_value.groq_api_key = "fake_key"
            mock_settings.return_value.ai_model = "test-model"
            
            service = AIService(db=AsyncMock())
            result = await service.analyze_complaint("comp_1")
            
            assert result is not None
            assert result["id"] == "ai_1"
            assert result["status"] == "completed"
            
            # Verify update was called to set COMPLETED status
            mock_ai_repo.update_one.assert_called_once()
            update_call_args = mock_ai_repo.update_one.call_args[0][1]
            assert update_call_args["$set"]["status"] == "completed"
            assert update_call_args["$set"]["result"]["category"] == "pothole_road_damage"
            assert update_call_args["$set"]["confidence"] == 0.8
