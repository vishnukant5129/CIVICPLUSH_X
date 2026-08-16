"""
CivicPulse AI — Predictive Intelligence Schemas.

Domain models for risk forecasting, category trend prediction,
spatial hotspot analysis, model evaluation, and data sufficiency state.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict

from app.domain.enums import CivicCategory


class PredictionType(str, Enum):
    CATEGORY_FORECAST = "category_forecast"
    HOTSPOT_RISK = "hotspot_risk"
    VOLUME_TREND = "volume_trend"
    ANOMALY_DETECTION = "anomaly_detection"


class PredictionStatus(str, Enum):
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class TrendDirection(str, Enum):
    INCREASING = "INCREASING"
    STABLE = "STABLE"
    DECREASING = "DECREASING"


class TimeSeriesPoint(BaseModel):
    date: str = Field(description="Date string formatted as YYYY-MM-DD")
    historical_count: int = Field(default=0, ge=0)
    predicted_count: Optional[float] = Field(default=None, ge=0.0)
    baseline_count: Optional[float] = Field(default=None, ge=0.0)


class CategoryForecast(BaseModel):
    category: str
    historical_count: int = Field(ge=0)
    forecast_count: float = Field(ge=0.0)
    trend_direction: TrendDirection
    growth_rate_pct: float
    status: PredictionStatus
    data_sufficiency_note: str


class HotspotItem(BaseModel):
    grid_id: str
    latitude: float
    longitude: float
    radius_meters: float = Field(default=1100.0, gt=0)
    complaint_count: int = Field(ge=1)
    risk_score: float = Field(ge=0.0, le=100.0, description="Normalized risk/activity score 0-100")
    primary_category: str
    trend_direction: TrendDirection


class EvaluationMetrics(BaseModel):
    mae: float = Field(description="Mean Absolute Error of model")
    rmse: float = Field(description="Root Mean Squared Error of model")
    baseline_mae: float = Field(description="Mean Absolute Error of naive baseline model")
    baseline_comparison: str = Field(description="Explanation of model performance vs baseline")


class DataWindow(BaseModel):
    start_date: str
    end_date: str
    observation_count: int = Field(ge=0)


class PredictionDocument(BaseModel):
    """Internal MongoDB prediction record schema."""
    id: Optional[str] = Field(default=None, alias="_id")
    prediction_id: str
    prediction_type: PredictionType
    status: PredictionStatus
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    data_window: DataWindow
    model_version: str
    model_type: str
    forecast_horizon_days: int
    overall_trend: Optional[TrendDirection] = None
    category_forecasts: List[CategoryForecast] = Field(default_factory=list)
    hotspots: List[HotspotItem] = Field(default_factory=list)
    time_series: List[TimeSeriesPoint] = Field(default_factory=list)
    evaluation: Optional[EvaluationMetrics] = None
    explanation: str
    limitations_note: str

    model_config = ConfigDict(populate_by_name=True)


class PredictionResponse(BaseModel):
    """Public API response schema for predictions."""
    prediction_id: str
    prediction_type: PredictionType
    status: PredictionStatus
    generated_at: datetime
    data_window: DataWindow
    model_version: str
    model_type: str
    forecast_horizon_days: int
    overall_trend: Optional[TrendDirection] = None
    category_forecasts: List[CategoryForecast] = Field(default_factory=list)
    hotspots: List[HotspotItem] = Field(default_factory=list)
    time_series: List[TimeSeriesPoint] = Field(default_factory=list)
    evaluation: Optional[EvaluationMetrics] = None
    explanation: str
    limitations_note: str
