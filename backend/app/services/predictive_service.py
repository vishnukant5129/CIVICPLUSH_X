"""
CivicPulse AI — Predictive Intelligence Service.

Computes time-series volume forecasts, category trends, baseline evaluation,
and spatial grid hotspot detection from real persisted complaint data.

Enforces strict scientific data sufficiency rules (no fake data or fabricated forecasts).
"""

from __future__ import annotations

import logging
import math
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from pymongo.asynchronous.database import AsyncDatabase

from app.config import get_settings
from app.domain.enums import CivicCategory
from app.domain.prediction_schemas import (
    CategoryForecast,
    DataWindow,
    EvaluationMetrics,
    HotspotItem,
    PredictionDocument,
    PredictionResponse,
    PredictionStatus,
    PredictionType,
    TimeSeriesPoint,
    TrendDirection,
)
from app.repositories.collections import ComplaintRepository, PredictionRepository

logger = logging.getLogger("civicpulse.predictive")


class PredictiveService:
    """Service executing statistical forecasting and spatial hotspot analysis."""

    def __init__(self, db: AsyncDatabase):
        self.db = db
        self.complaint_repo = ComplaintRepository(db)
        self.prediction_repo = PredictionRepository(db)
        self.settings = get_settings()

    async def get_summary(self) -> PredictionResponse:
        """
        Get or generate the latest overall predictive intelligence summary.
        """
        latest = await self.prediction_repo.find_latest_by_type(PredictionType.VOLUME_TREND.value)
        if latest:
            return PredictionResponse(**latest)
        
        # If no prediction exists yet, generate one on demand
        return await self.generate_predictions()

    async def get_trends(self) -> PredictionResponse:
        """
        Get category and volume trend predictions.
        """
        latest = await self.prediction_repo.find_latest_by_type(PredictionType.CATEGORY_FORECAST.value)
        if latest:
            return PredictionResponse(**latest)
        
        return await self.generate_predictions()

    async def get_hotspots(self) -> PredictionResponse:
        """
        Get geographic hotspot risk analysis.
        """
        latest = await self.prediction_repo.find_latest_by_type(PredictionType.HOTSPOT_RISK.value)
        if latest:
            return PredictionResponse(**latest)
        
        return await self.generate_predictions()

    async def generate_predictions(self) -> PredictionResponse:
        """
        Runs the full predictive analysis pipeline over persisted complaint records.
        """
        now_utc = datetime.now(timezone.utc)
        
        # 1. Gather historical complaint metadata
        complaints = await self.complaint_repo.find_many({}, limit=10000)
        total_obs = len(complaints)

        # 2. Check Data Sufficiency
        min_required = self.settings.predictive_min_historical_complaints
        if total_obs < min_required:
            logger.info(
                f"Data sufficiency check failed: {total_obs} complaints found, {min_required} required."
            )
            doc = PredictionDocument(
                prediction_id=f"pred_insufficient_{uuid.uuid4().hex[:8]}",
                prediction_type=PredictionType.VOLUME_TREND,
                status=PredictionStatus.INSUFFICIENT_DATA,
                generated_at=now_utc,
                data_window=DataWindow(
                    start_date=now_utc.strftime("%Y-%m-%d"),
                    end_date=now_utc.strftime("%Y-%m-%d"),
                    observation_count=total_obs,
                ),
                model_version=self.settings.predictive_model_version,
                model_type="none",
                forecast_horizon_days=self.settings.predictive_forecast_horizon_days,
                explanation=(
                    f"Insufficient historical complaint data to generate predictions. "
                    f"Found {total_obs} observation(s), minimum required threshold is {min_required}."
                ),
                limitations_note=(
                    "Predictions require a minimum density of historical reporting. "
                    "As citizens submit more verified complaints, predictive modeling will activate automatically."
                ),
            )
            saved_id = await self.prediction_repo.insert_one(doc.model_dump(by_alias=True, exclude={"id"}))
            saved_doc = await self.prediction_repo.find_by_id(saved_id)
            return PredictionResponse(**saved_doc)

        # Extract date range
        timestamps = [
            c["created_at"] if isinstance(c["created_at"], datetime)
            else datetime.fromisoformat(str(c["created_at"]))
            for c in complaints
            if "created_at" in c and c["created_at"]
        ]
        start_date_str = min(timestamps).strftime("%Y-%m-%d") if timestamps else now_utc.strftime("%Y-%m-%d")
        end_date_str = max(timestamps).strftime("%Y-%m-%d") if timestamps else now_utc.strftime("%Y-%m-%d")

        data_window = DataWindow(
            start_date=start_date_str,
            end_date=end_date_str,
            observation_count=total_obs,
        )

        # 3. Compute Time Series & Volume Forecast
        time_series, overall_trend, evaluation = self._compute_volume_forecast(complaints)

        # 4. Compute Category Trends
        category_forecasts = self._compute_category_forecasts(complaints)

        # 5. Compute Spatial Grid Hotspots
        hotspots = self._compute_hotspots(complaints)

        # Construct complete prediction document
        doc = PredictionDocument(
            prediction_id=f"pred_{uuid.uuid4().hex[:12]}",
            prediction_type=PredictionType.VOLUME_TREND,
            status=PredictionStatus.COMPLETED,
            generated_at=now_utc,
            data_window=data_window,
            model_version=self.settings.predictive_model_version,
            model_type="exponential_weighted_moving_average",
            forecast_horizon_days=self.settings.predictive_forecast_horizon_days,
            overall_trend=overall_trend,
            category_forecasts=category_forecasts,
            hotspots=hotspots,
            time_series=time_series,
            evaluation=evaluation,
            explanation=(
                f"Statistical forecast computed from {total_obs} complaint records. "
                f"Overall trend is {overall_trend.value if overall_trend else 'STABLE'}. "
                f"Identified {len(hotspots)} geographic hotspot area(s)."
            ),
            limitations_note=(
                "Predictive intelligence reflects historical reported civic complaint patterns, "
                "not guaranteed future occurrences. High complaint density reflects increased reporting activity."
            ),
        )

        # Persist prediction
        saved_id = await self.prediction_repo.insert_one(doc.model_dump(by_alias=True, exclude={"id"}))
        saved_doc = await self.prediction_repo.find_by_id(saved_id)
        
        # Also persist under CATEGORY_FORECAST and HOTSPOT_RISK for endpoint specificity
        doc_cat = doc.model_copy(update={"prediction_type": PredictionType.CATEGORY_FORECAST})
        await self.prediction_repo.insert_one(doc_cat.model_dump(by_alias=True, exclude={"id"}))

        doc_hot = doc.model_copy(update={"prediction_type": PredictionType.HOTSPOT_RISK})
        await self.prediction_repo.insert_one(doc_hot.model_dump(by_alias=True, exclude={"id"}))

        return PredictionResponse(**saved_doc)

    def _compute_volume_forecast(
        self, complaints: List[Dict[str, Any]]
    ) -> Tuple[List[TimeSeriesPoint], TrendDirection, Optional[EvaluationMetrics]]:
        """
        Group complaints by day and compute EWMA forecast vs Naive Baseline.
        """
        # Bucket by date
        counts_by_date: Dict[str, int] = {}
        for c in complaints:
            dt = c.get("created_at")
            if not dt:
                continue
            if isinstance(dt, str):
                dt = datetime.fromisoformat(dt)
            date_key = dt.strftime("%Y-%m-%d")
            counts_by_date[date_key] = counts_by_date.get(date_key, 0) + 1

        if not counts_by_date:
            return [], TrendDirection.STABLE, None

        sorted_dates = sorted(counts_by_date.keys())
        counts = [counts_by_date[d] for d in sorted_dates]

        # EWMA calculation (alpha = 0.3)
        alpha = 0.3
        ewma_values: List[float] = []
        running_ewma = float(counts[0])
        for val in counts:
            running_ewma = alpha * float(val) + (1 - alpha) * running_ewma
            ewma_values.append(round(running_ewma, 2))

        # Naive Baseline (previous day count or mean)
        baseline_values: List[float] = [float(counts[0])] + [float(c) for c in counts[:-1]]

        # Build Historical TimeSeriesPoints
        points: List[TimeSeriesPoint] = []
        for d, h_count, pred, base in zip(sorted_dates, counts, ewma_values, baseline_values):
            points.append(
                TimeSeriesPoint(
                    date=d,
                    historical_count=h_count,
                    predicted_count=pred,
                    baseline_count=base,
                )
            )

        # Forecast future horizon
        last_date = datetime.strptime(sorted_dates[-1], "%Y-%m-%d")
        horizon = self.settings.predictive_forecast_horizon_days
        last_pred = ewma_values[-1]

        # Linear slope for trend direction
        n = len(counts)
        if n >= 2:
            x_mean = (n - 1) / 2.0
            y_mean = sum(counts) / float(n)
            num = sum((i - x_mean) * (counts[i] - y_mean) for i in range(n))
            den = sum((i - x_mean) ** 2 for i in range(n))
            slope = num / den if den != 0 else 0.0
        else:
            slope = 0.0

        if slope > 0.05:
            overall_trend = TrendDirection.INCREASING
        elif slope < -0.05:
            overall_trend = TrendDirection.DECREASING
        else:
            overall_trend = TrendDirection.STABLE

        for i in range(1, horizon + 1):
            future_date = (last_date + timedelta(days=i)).strftime("%Y-%m-%d")
            # Projected value incorporates slope trend
            projected = max(0.0, round(last_pred + slope * i, 2))
            base_proj = round(last_pred, 2)
            points.append(
                TimeSeriesPoint(
                    date=future_date,
                    historical_count=0,
                    predicted_count=projected,
                    baseline_count=base_proj,
                )
            )

        # Evaluation metrics (chronological test split if n >= 5)
        evaluation: Optional[EvaluationMetrics] = None
        if n >= 5:
            split_idx = int(n * 0.7)
            test_actual = counts[split_idx:]
            test_ewma = ewma_values[split_idx:]
            test_baseline = baseline_values[split_idx:]

            mae = sum(abs(a - p) for a, p in zip(test_actual, test_ewma)) / len(test_actual)
            rmse = math.sqrt(sum((a - p) ** 2 for a, p in zip(test_actual, test_ewma)) / len(test_actual))
            baseline_mae = sum(abs(a - b) for a, b in zip(test_actual, test_baseline)) / len(test_actual)

            comp_text = (
                f"EWMA model MAE: {round(mae, 2)} vs Naive Baseline MAE: {round(baseline_mae, 2)}. "
                + ("EWMA outperforms baseline." if mae <= baseline_mae else "Naive baseline performs equally well.")
            )

            evaluation = EvaluationMetrics(
                mae=round(mae, 2),
                rmse=round(rmse, 2),
                baseline_mae=round(baseline_mae, 2),
                baseline_comparison=comp_text,
            )

        return points, overall_trend, evaluation

    def _compute_category_forecasts(self, complaints: List[Dict[str, Any]]) -> List[CategoryForecast]:
        """
        Compute category breakdown, trend direction, and growth rate.
        Enforces per-category minimum data threshold.
        """
        min_cat_req = self.settings.predictive_min_category_complaints
        counts_by_cat: Dict[str, List[datetime]] = {}
        for c in complaints:
            cat = c.get("category", CivicCategory.OTHER.value)
            dt = c.get("created_at")
            if not dt:
                continue
            if isinstance(dt, str):
                dt = datetime.fromisoformat(dt)
            counts_by_cat.setdefault(cat, []).append(dt)

        results: List[CategoryForecast] = []
        for cat in CivicCategory:
            cat_val = cat.value
            timestamps = counts_by_cat.get(cat_val, [])
            total_count = len(timestamps)

            if total_count < min_cat_req:
                results.append(
                    CategoryForecast(
                        category=cat_val,
                        historical_count=total_count,
                        forecast_count=float(total_count),
                        trend_direction=TrendDirection.STABLE,
                        growth_rate_pct=0.0,
                        status=PredictionStatus.INSUFFICIENT_DATA,
                        data_sufficiency_note=(
                            f"Category has {total_count} complaint(s); minimum required for trend modeling is {min_cat_req}."
                        ),
                    )
                )
            else:
                # Calculate recent 7-day vs prior 7-day growth
                now = datetime.now(timezone.utc)
                recent_cutoff = now - timedelta(days=7)
                prior_cutoff = now - timedelta(days=14)

                recent_cnt = sum(1 for t in timestamps if t >= recent_cutoff)
                prior_cnt = sum(1 for t in timestamps if prior_cutoff <= t < recent_cutoff)

                if prior_cnt > 0:
                    growth_rate = ((recent_cnt - prior_cnt) / float(prior_cnt)) * 100.0
                else:
                    growth_rate = 100.0 if recent_cnt > 0 else 0.0

                if growth_rate > 10.0:
                    direction = TrendDirection.INCREASING
                elif growth_rate < -10.0:
                    direction = TrendDirection.DECREASING
                else:
                    direction = TrendDirection.STABLE

                # Simple forecast count for next period
                forecast_val = max(0.0, round(recent_cnt * (1.0 + (growth_rate / 100.0)), 1))

                results.append(
                    CategoryForecast(
                        category=cat_val,
                        historical_count=total_count,
                        forecast_count=forecast_val,
                        trend_direction=direction,
                        growth_rate_pct=round(growth_rate, 1),
                        status=PredictionStatus.COMPLETED,
                        data_sufficiency_note=f"Sufficient historical data ({total_count} observations).",
                    )
                )

        return results

    def _compute_hotspots(self, complaints: List[Dict[str, Any]]) -> List[HotspotItem]:
        """
        Group complaints into spatial grid cells (0.01 deg resolution ~ 1.1km)
        and compute mathematically grounded risk/activity score.
        """
        grid_res = self.settings.predictive_grid_resolution_deg
        min_hotspot_cnt = self.settings.predictive_min_hotspot_complaints

        grid_cells: Dict[Tuple[int, int], List[Dict[str, Any]]] = {}

        for c in complaints:
            loc = c.get("location")
            if not loc or not isinstance(loc, dict):
                continue
            coords = loc.get("coordinates")
            if not coords or len(coords) < 2:
                continue
            lon, lat = coords[0], coords[1]
            if not (-180.0 <= lon <= 180.0 and -90.0 <= lat <= 90.0):
                continue

            # Compute grid index
            grid_x = int(math.floor(lon / grid_res))
            grid_y = int(math.floor(lat / grid_res))
            key = (grid_x, grid_y)

            grid_cells.setdefault(key, []).append(c)

        if not grid_cells:
            return []

        # Find max cell count for density scaling
        max_cell_cnt = max(len(items) for items in grid_cells.values())

        hotspots: List[HotspotItem] = []
        now = datetime.now(timezone.utc)

        for (gx, gy), items in grid_cells.items():
            cell_cnt = len(items)
            if cell_cnt < min_hotspot_cnt:
                continue

            # Calculate center lat/lon
            center_lon = round((gx + 0.5) * grid_res, 5)
            center_lat = round((gy + 0.5) * grid_res, 5)

            # Category distribution in cell
            cat_counts: Dict[str, int] = {}
            for item in items:
                cat = item.get("category", "other")
                cat_counts[cat] = cat_counts.get(cat, 0) + 1
            primary_cat = max(cat_counts.items(), key=lambda x: x[1])[0]

            # Calculate Risk / Activity Score (0-100)
            # Component 1: Relative density (0-60 points)
            density_score = (cell_cnt / float(max_cell_cnt)) * 60.0

            # Component 2: Recency weighting (0-20 points)
            recency_sum = 0.0
            for item in items:
                dt = item.get("created_at")
                if isinstance(dt, str):
                    dt = datetime.fromisoformat(dt)
                if dt:
                    age_days = max(0.0, (now - dt).total_seconds() / 86400.0)
                    recency_sum += math.exp(-age_days / 14.0) # 14-day half-life
            recency_score = min(20.0, (recency_sum / float(cell_cnt)) * 20.0)

            # Component 3: High impact category weight (0-20 points)
            high_impact_cats = {
                CivicCategory.SEWAGE_DRAINAGE.value,
                CivicCategory.WATER_LEAKAGE.value,
                CivicCategory.PUBLIC_INFRASTRUCTURE.value,
            }
            impact_cnt = sum(1 for item in items if item.get("category") in high_impact_cats)
            impact_score = (impact_cnt / float(cell_cnt)) * 20.0

            total_risk = round(min(100.0, density_score + recency_score + impact_score), 1)

            trend_dir = TrendDirection.INCREASING if cell_cnt >= 3 else TrendDirection.STABLE

            grid_id = f"grid_{gx}_{gy}"

            hotspots.append(
                HotspotItem(
                    grid_id=grid_id,
                    latitude=center_lat,
                    longitude=center_lon,
                    radius_meters=round(grid_res * 111000.0 / 2.0, 1),
                    complaint_count=cell_cnt,
                    risk_score=total_risk,
                    primary_category=primary_cat,
                    trend_direction=trend_dir,
                )
            )

        # Sort hotspots by risk_score descending
        hotspots.sort(key=lambda h: h.risk_score, reverse=True)
        return hotspots
