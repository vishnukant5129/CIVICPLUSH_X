import React, { useState, useEffect } from 'react';
import { predictionsApi } from '../api/predictions';
import type { PredictionResponse } from '../api/predictions';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/Card';
import { Badge } from './ui/Badge';
import { Button } from './ui/Button';
import { BrainCircuit, AlertTriangle, TrendingUp, TrendingDown, ArrowRight, Zap, Loader2, Database, ShieldAlert, Activity } from 'lucide-react';

export const PredictiveIntelligence: React.FC = () => {
  const { user } = useAuth();
  const [data, setData] = useState<PredictionResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);

  const fetchPredictions = async () => {
    setLoading(true);
    setError(null);
    try {
      const summary = await predictionsApi.getSummary();
      setData(summary);
    } catch (err: any) {
      setError(err.message || 'Failed to load predictive intelligence.');
    } finally {
      setLoading(false);
    }
  };

  const handleRunPipeline = async () => {
    setGenerating(true);
    try {
      const updated = await predictionsApi.generatePredictions();
      setData(updated);
    } catch (err: any) {
      alert(err.message || 'Failed to trigger predictive pipeline.');
    } finally {
      setGenerating(false);
    }
  };

  useEffect(() => {
    fetchPredictions();
  }, []);

  const isAuthority = user?.role === 'authority' || user?.role === 'admin';

  if (loading) {
    return (
      <Card className="border-dashed border-2 bg-gray-50/50">
        <CardContent className="flex flex-col items-center justify-center py-12 space-y-4">
          <Loader2 className="h-8 w-8 text-civic-600 animate-spin" />
          <p className="text-gray-500 font-medium text-center max-w-sm">Analyzing complaint time-series & spatial risk patterns...</p>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="border-red-200 bg-red-50">
        <CardContent className="flex flex-col items-center justify-center py-8 space-y-4">
          <AlertTriangle className="h-10 w-10 text-red-500" />
          <h3 className="font-bold text-red-900 text-lg">Predictive Intelligence Error</h3>
          <p className="text-red-700 text-center text-sm">{error}</p>
        </CardContent>
      </Card>
    );
  }

  if (!data) return null;

  return (
    <div className="space-y-6">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <BrainCircuit className="h-6 w-6 text-civic-600" />
            Predictive Civic Intelligence
          </h2>
          <p className="text-sm text-gray-500 mt-1">
            Data-driven forecasting and risk analysis derived from verified complaint activity.
          </p>
        </div>
        {isAuthority && (
          <Button
            onClick={handleRunPipeline}
            disabled={generating}
            className="flex-shrink-0"
          >
            {generating ? (
              <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Running Analysis</>
            ) : (
              <><Zap className="mr-2 h-4 w-4" /> Run Predictive Pipeline</>
            )}
          </Button>
        )}
      </div>

      {/* Data Sufficiency Check Banner */}
      {data.status === 'INSUFFICIENT_DATA' ? (
        <Card className="border-amber-200 bg-amber-50 shadow-sm">
          <CardContent className="p-6">
            <div className="flex items-start gap-4">
              <div className="bg-amber-100 p-3 rounded-full">
                <Database className="h-6 w-6 text-amber-600" />
              </div>
              <div className="flex-1 space-y-1">
                <h3 className="font-semibold text-lg text-amber-900">Insufficient Historical Data</h3>
                <p className="text-sm text-amber-800">{data.explanation}</p>
                <div className="mt-4 pt-4 border-t border-amber-200/60 text-xs text-amber-800 flex flex-col sm:flex-row gap-4">
                  <div><strong>Observation Count:</strong> {data.data_window.observation_count} complaint(s)</div>
                  <div><strong>Policy Note:</strong> {data.limitations_note}</div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      ) : (
        <>
          {/* Overview Metrics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardContent className="p-5">
                <div className="flex items-center gap-2 mb-2">
                  <Activity className="h-4 w-4 text-gray-400" />
                  <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Overall Trend</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-2xl font-bold text-gray-900">{data.overall_trend || 'STABLE'}</span>
                  {data.overall_trend === 'INCREASING' && <TrendingUp className="h-6 w-6 text-red-500" />}
                  {data.overall_trend === 'DECREASING' && <TrendingDown className="h-6 w-6 text-green-500" />}
                  {data.overall_trend === 'STABLE' && <ArrowRight className="h-6 w-6 text-gray-400" />}
                </div>
                <p className="text-xs text-gray-500 mt-2">Calculated over historical complaint volume</p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-5">
                <div className="flex items-center gap-2 mb-2">
                  <Database className="h-4 w-4 text-gray-400" />
                  <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Observation Window</span>
                </div>
                <div className="text-2xl font-bold text-gray-900">
                  {data.data_window.observation_count} Records
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  {data.data_window.start_date} to {data.data_window.end_date}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-5">
                <div className="flex items-center gap-2 mb-2">
                  <BrainCircuit className="h-4 w-4 text-gray-400" />
                  <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Model Specification</span>
                </div>
                <div className="text-xl font-bold text-gray-900 truncate" title={data.model_type}>
                  {data.model_type}
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  Version {data.model_version} • {data.forecast_horizon_days}-Day Horizon
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Model Evaluation & Scientific Honesty Note */}
          {data.evaluation && (
            <div className="bg-civic-50 border border-civic-100 rounded-lg p-4 text-xs text-civic-900 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
              <div className="flex items-center gap-2">
                <ShieldAlert className="h-4 w-4 text-civic-600 flex-shrink-0" />
                <span><strong>Model Evaluation:</strong> {data.evaluation.baseline_comparison}</span>
              </div>
              <div className="font-mono text-xs opacity-75">
                MAE: {data.evaluation.mae} | RMSE: {data.evaluation.rmse} | Base: {data.evaluation.baseline_mae}
              </div>
            </div>
          )}

          {/* Category Forecasts */}
          {data.category_forecasts.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Category Volume Forecasts</CardTitle>
                <CardDescription>Predicted incoming complaint volumes for the next {data.forecast_horizon_days} days</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
                  {data.category_forecasts.map((cat) => (
                    <div key={cat.category} className="p-4 rounded-lg border border-gray-100 bg-gray-50 hover:bg-gray-100/50 transition-colors">
                      <div className="text-xs font-bold text-gray-600 uppercase tracking-wider truncate mb-2">
                        {cat.category.replace(/_/g, ' ')}
                      </div>
                      {cat.status === 'INSUFFICIENT_DATA' ? (
                        <div className="flex items-center gap-1.5 text-amber-600 mt-3">
                          <AlertTriangle className="h-4 w-4" />
                          <span className="text-xs font-medium">Insufficient Data ({cat.historical_count} records)</span>
                        </div>
                      ) : (
                        <>
                          <div className="flex justify-between items-baseline">
                            <span className="text-2xl font-bold text-gray-900">{cat.forecast_count}</span>
                            <Badge 
                              variant={cat.growth_rate_pct > 0 ? "destructive" : cat.growth_rate_pct < 0 ? "success" : "secondary"}
                              className="text-[10px] px-1.5"
                            >
                              {cat.growth_rate_pct > 0 ? '+' : ''}{cat.growth_rate_pct}%
                            </Badge>
                          </div>
                          <div className="text-[11px] text-gray-500 mt-2 flex justify-between">
                            <span>Hist: {cat.historical_count}</span>
                            <span className="capitalize">Trend: {cat.trend_direction}</span>
                          </div>
                        </>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Spatial Grid Hotspots (Authorized operational personnel) */}
          {isAuthority && data.hotspots.length > 0 && (
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <div className="space-y-1">
                  <CardTitle className="text-lg">Operational Spatial Hotspots</CardTitle>
                  <CardDescription>High-risk geographic clusters</CardDescription>
                </div>
                <Badge variant="destructive" className="hidden sm:inline-flex">Restricted Authority View</Badge>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto rounded-md border border-gray-100">
                  <table className="min-w-full text-left text-sm text-gray-600">
                    <thead className="bg-gray-50 text-xs uppercase font-semibold text-gray-500 border-b">
                      <tr>
                        <th className="px-4 py-3 whitespace-nowrap">Grid ID</th>
                        <th className="px-4 py-3 whitespace-nowrap">Center Coordinates</th>
                        <th className="px-4 py-3 text-center whitespace-nowrap">Complaints</th>
                        <th className="px-4 py-3 whitespace-nowrap">Primary Category</th>
                        <th className="px-4 py-3 text-right whitespace-nowrap">Risk Score</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100 bg-white">
                      {data.hotspots.map((hotspot) => (
                        <tr key={hotspot.grid_id} className="hover:bg-gray-50/50">
                          <td className="px-4 py-3 font-mono text-xs">{hotspot.grid_id}</td>
                          <td className="px-4 py-3 text-xs">
                            {hotspot.latitude.toFixed(4)}, {hotspot.longitude.toFixed(4)} <span className="text-gray-400">(~{hotspot.radius_meters}m)</span>
                          </td>
                          <td className="px-4 py-3 font-semibold text-gray-900 text-center">{hotspot.complaint_count}</td>
                          <td className="px-4 py-3 text-xs capitalize">{hotspot.primary_category.replace(/_/g, ' ')}</td>
                          <td className="px-4 py-3 text-right">
                            <Badge 
                              variant={hotspot.risk_score >= 70 ? 'destructive' : hotspot.risk_score >= 40 ? 'warning' : 'info'}
                            >
                              {hotspot.risk_score} / 100
                            </Badge>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Time Series Table */}
          {data.time_series.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Historical & Projected Volume</CardTitle>
                <CardDescription>Daily complaint time-series data</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto rounded-md border border-gray-100">
                  <table className="min-w-full text-left text-sm text-gray-600">
                    <thead className="bg-gray-50 text-xs uppercase font-semibold text-gray-500 border-b">
                      <tr>
                        <th className="px-4 py-3">Date</th>
                        <th className="px-4 py-3 text-center">Observed Count</th>
                        <th className="px-4 py-3 text-center">Forecast (EWMA)</th>
                        <th className="px-4 py-3 text-center text-gray-400">Baseline</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100 bg-white">
                      {data.time_series.map((point) => (
                        <tr key={point.date} className="hover:bg-gray-50/50">
                          <td className="px-4 py-3 font-medium text-gray-900">{point.date}</td>
                          <td className="px-4 py-3 text-center">{point.historical_count > 0 ? point.historical_count : '—'}</td>
                          <td className="px-4 py-3 font-semibold text-civic-600 text-center">
                            {point.predicted_count !== undefined ? point.predicted_count : '—'}
                          </td>
                          <td className="px-4 py-3 text-gray-400 text-center">
                            {point.baseline_count !== undefined ? point.baseline_count : '—'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  );
};
