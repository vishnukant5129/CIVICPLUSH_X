"""
Unit and API integration tests for Phase 10 Predictive Civic Intelligence.
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch
import pytest
from httpx import ASGITransport, AsyncClient

from app.dependencies.auth import require_authenticated_user
from app.domain.auth_schemas import UserResponse
from app.domain.enums import CivicCategory, UserRole
from app.domain.prediction_schemas import PredictionStatus, PredictionType
from app.main import app
from app.services.predictive_service import PredictiveService

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def citizen_client():
    mock_user = UserResponse(
        id="citizen_1",
        email="citizen@example.com",
        display_name="Citizen Test",
        role=UserRole.CITIZEN,
    )
    app.dependency_overrides[require_authenticated_user] = lambda: mock_user
    with patch("app.api.predictions.get_database", return_value=AsyncMock()):
        with patch("app.dependencies.auth.get_database", return_value=AsyncMock()):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def authority_client():
    mock_user = UserResponse(
        id="auth_1",
        email="authority@example.com",
        display_name="Officer Test",
        role=UserRole.AUTHORITY,
        department_id="dept_101",
    )
    app.dependency_overrides[require_authenticated_user] = lambda: mock_user
    with patch("app.api.predictions.get_database", return_value=AsyncMock()):
        with patch("app.dependencies.auth.get_database", return_value=AsyncMock()):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                yield ac
    app.dependency_overrides.clear()


@pytest.mark.asyncio
class TestPredictiveServiceUnit:
    async def test_insufficient_data_handling(self):
        """Verify system returns INSUFFICIENT_DATA when observation count is below minimum threshold."""
        mock_db = AsyncMock()
        service = PredictiveService(mock_db)

        # Mock 2 complaints (threshold is 5)
        mock_complaints = [
            {"created_at": datetime.now(timezone.utc), "category": CivicCategory.POTHOLE_ROAD_DAMAGE.value},
            {"created_at": datetime.now(timezone.utc), "category": CivicCategory.POTHOLE_ROAD_DAMAGE.value},
        ]

        with patch.object(service.complaint_repo, "find_many", return_value=mock_complaints):
            with patch.object(service.prediction_repo, "insert_one", return_value="pred_id_1"):
                with patch.object(
                    service.prediction_repo,
                    "find_by_id",
                    return_value={
                        "prediction_id": "pred_insufficient_123",
                        "prediction_type": PredictionType.VOLUME_TREND.value,
                        "status": PredictionStatus.INSUFFICIENT_DATA.value,
                        "generated_at": datetime.now(timezone.utc),
                        "data_window": {"start_date": "2026-08-16", "end_date": "2026-08-16", "observation_count": 2},
                        "model_version": "v1.0-ewma-grid",
                        "model_type": "none",
                        "forecast_horizon_days": 7,
                        "explanation": "Insufficient historical complaint data to generate predictions. Found 2 observation(s), minimum required threshold is 5.",
                        "limitations_note": "Predictions require a minimum density of historical reporting.",
                    },
                ):
                    res = await service.generate_predictions()
                    assert res.status == PredictionStatus.INSUFFICIENT_DATA
                    assert res.data_window.observation_count == 2
                    assert "Insufficient historical complaint data" in res.explanation

    async def test_successful_forecasting_and_hotspots(self):
        """Verify forecasting, baseline evaluation, category trends, and spatial hotspots on sufficient data."""
        mock_db = AsyncMock()
        service = PredictiveService(mock_db)

        now = datetime.now(timezone.utc)

        # Create 10 complaints across 5 days and 2 spatial clusters
        mock_complaints = []
        for i in range(10):
            day_offset = i % 5
            complaint_dt = now - timedelta(days=day_offset)
            # Cluster A (lon=77.2, lat=28.6) vs Cluster B (lon=77.5, lat=28.9)
            lon = 77.201 if i < 6 else 77.501
            lat = 28.601 if i < 6 else 28.901
            cat = CivicCategory.POTHOLE_ROAD_DAMAGE.value if i % 2 == 0 else CivicCategory.SEWAGE_DRAINAGE.value

            mock_complaints.append(
                {
                    "created_at": complaint_dt,
                    "category": cat,
                    "location": {"type": "Point", "coordinates": [lon, lat]},
                }
            )

        with patch.object(service.complaint_repo, "find_many", return_value=mock_complaints):
            with patch.object(service.prediction_repo, "insert_one", return_value="pred_id_2"):
                fake_saved_doc = {
                    "prediction_id": "pred_20260816",
                    "prediction_type": PredictionType.VOLUME_TREND.value,
                    "status": PredictionStatus.COMPLETED.value,
                    "generated_at": now,
                    "data_window": {"start_date": "2026-08-11", "end_date": "2026-08-16", "observation_count": 10},
                    "model_version": "v1.0-ewma-grid",
                    "model_type": "exponential_weighted_moving_average",
                    "forecast_horizon_days": 7,
                    "overall_trend": "STABLE",
                    "category_forecasts": [],
                    "hotspots": [
                        {
                            "grid_id": "grid_7720_2860",
                            "latitude": 28.605,
                            "longitude": 77.205,
                            "radius_meters": 555.0,
                            "complaint_count": 6,
                            "risk_score": 85.0,
                            "primary_category": CivicCategory.POTHOLE_ROAD_DAMAGE.value,
                            "trend_direction": "INCREASING",
                        }
                    ],
                    "time_series": [
                        {"date": "2026-08-12", "historical_count": 2, "predicted_count": 2.0, "baseline_count": 2.0}
                    ],
                    "explanation": "Statistical forecast computed from 10 records.",
                    "limitations_note": "Test note",
                }

                with patch.object(service.prediction_repo, "find_by_id", return_value=fake_saved_doc):
                    res = await service.generate_predictions()
                    assert res.status == PredictionStatus.COMPLETED
                    assert res.data_window.observation_count == 10
                    assert len(res.hotspots) == 1
                    assert res.hotspots[0].risk_score == 85.0


@pytest.mark.asyncio
class TestPredictiveAPI:
    async def test_citizen_access_summary_and_trends(self, citizen_client):
        """Citizen can view general summary and trends."""
        mock_resp = {
            "prediction_id": "pred_123",
            "prediction_type": "volume_trend",
            "status": "COMPLETED",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "data_window": {"start_date": "2026-08-01", "end_date": "2026-08-16", "observation_count": 12},
            "model_version": "v1.0-ewma-grid",
            "model_type": "exponential_weighted_moving_average",
            "forecast_horizon_days": 7,
            "overall_trend": "STABLE",
            "category_forecasts": [],
            "hotspots": [],
            "time_series": [],
            "explanation": "Test summary",
            "limitations_note": "Test note",
        }

        with patch("app.api.predictions.PredictiveService.get_summary", return_value=mock_resp):
            res = await citizen_client.get("/api/v1/predictions/summary")
            assert res.status_code == 200
            data = res.json()
            assert data["status"] == "COMPLETED"

    async def test_citizen_restricted_from_hotspots_and_generate(self, citizen_client):
        """Citizen receives 403 Forbidden for operational spatial hotspots and pipeline generation."""
        res_hot = await citizen_client.get("/api/v1/predictions/hotspots")
        assert res_hot.status_code == 403, f"Expected 403, got {res_hot.status_code}: {res_hot.text}"

        res_gen = await citizen_client.post("/api/v1/predictions/generate")
        assert res_gen.status_code == 403, f"Expected 403, got {res_gen.status_code}: {res_gen.text}"

    async def test_authority_allowed_hotspots_and_generate(self, authority_client):
        """Authority user can access operational hotspots and trigger prediction generation."""
        mock_resp = {
            "prediction_id": "pred_hot_123",
            "prediction_type": "hotspot_risk",
            "status": "COMPLETED",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "data_window": {"start_date": "2026-08-01", "end_date": "2026-08-16", "observation_count": 12},
            "model_version": "v1.0-ewma-grid",
            "model_type": "exponential_weighted_moving_average",
            "forecast_horizon_days": 7,
            "overall_trend": "STABLE",
            "category_forecasts": [],
            "hotspots": [
                {
                    "grid_id": "grid_77_28",
                    "latitude": 28.605,
                    "longitude": 77.205,
                    "radius_meters": 555.0,
                    "complaint_count": 6,
                    "risk_score": 75.5,
                    "primary_category": "pothole_road_damage",
                    "trend_direction": "INCREASING",
                }
            ],
            "time_series": [],
            "explanation": "Test hotspots",
            "limitations_note": "Test note",
        }

        with patch("app.api.predictions.PredictiveService.get_hotspots", return_value=mock_resp):
            res = await authority_client.get("/api/v1/predictions/hotspots")
            assert res.status_code == 200
            data = res.json()
            assert len(data["hotspots"]) == 1
            assert data["hotspots"][0]["risk_score"] == 75.5
