import { apiFetch } from './client';

export type PredictionStatus = 'INSUFFICIENT_DATA' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
export type TrendDirection = 'INCREASING' | 'STABLE' | 'DECREASING';

export interface TimeSeriesPoint {
  date: string;
  historical_count: number;
  predicted_count: number | null;
  baseline_count: number | null;
}

export interface CategoryForecast {
  category: string;
  historical_count: number;
  forecast_count: number;
  trend_direction: TrendDirection;
  growth_rate_pct: number;
  status: PredictionStatus;
  data_sufficiency_note: string;
}

export interface HotspotItem {
  grid_id: string;
  latitude: number;
  longitude: number;
  radius_meters: number;
  complaint_count: number;
  risk_score: number;
  primary_category: string;
  trend_direction: TrendDirection;
}

export interface EvaluationMetrics {
  mae: number;
  rmse: number;
  baseline_mae: number;
  baseline_comparison: string;
}

export interface DataWindow {
  start_date: string;
  end_date: string;
  observation_count: number;
}

export interface PredictionResponse {
  prediction_id: string;
  prediction_type: string;
  status: PredictionStatus;
  generated_at: string;
  data_window: DataWindow;
  model_version: string;
  model_type: string;
  forecast_horizon_days: number;
  overall_trend: TrendDirection | null;
  category_forecasts: CategoryForecast[];
  hotspots: HotspotItem[];
  time_series: TimeSeriesPoint[];
  evaluation: EvaluationMetrics | null;
  explanation: string;
  limitations_note: string;
}

export const predictionsApi = {
  getSummary: async (): Promise<PredictionResponse> => {
    return apiFetch<PredictionResponse>('/api/v1/predictions/summary');
  },

  getTrends: async (): Promise<PredictionResponse> => {
    return apiFetch<PredictionResponse>('/api/v1/predictions/trends');
  },

  getHotspots: async (): Promise<PredictionResponse> => {
    return apiFetch<PredictionResponse>('/api/v1/predictions/hotspots');
  },

  generatePredictions: async (): Promise<PredictionResponse> => {
    return apiFetch<PredictionResponse>('/api/v1/predictions/generate', {
      method: 'POST',
    });
  },
};
