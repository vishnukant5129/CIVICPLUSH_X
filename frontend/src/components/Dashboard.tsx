import React, { useEffect, useState } from 'react';
import { dashboardApi } from '../api/dashboard';
import { complaintsApi } from '../api/complaints';
import { predictionsApi } from '../api/predictions';
import type { DashboardSummaryResponse, GeoJSONFeatureCollection, DashboardFilters } from '../api/dashboard';
import type { ComplaintResponse } from '../api/complaints';
import type { PredictionResponse } from '../api/predictions';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card';
import { Button } from './ui/Button';
import { 
  FileText, AlertTriangle, CheckCircle2, Clock, Map as MapIcon, 
  Loader2, Activity, Zap, BarChart3, Database, CloudRain, ShieldCheck, Hand
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

// Fix leaflet marker icon issues in React
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';
let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconAnchor: [12, 41],
});
L.Marker.prototype.options.icon = DefaultIcon;

const CATEGORY_COLORS = ['#3b82f6', '#22c55e', '#eab308', '#a855f7', '#94a3b8'];

export const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [summary, setSummary] = useState<DashboardSummaryResponse | null>(null);
  const [mapData, setMapData] = useState<GeoJSONFeatureCollection | null>(null);
  const [recentComplaints, setRecentComplaints] = useState<ComplaintResponse[]>([]);
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isFullMapOpen, setIsFullMapOpen] = useState(false);

  const filters: DashboardFilters = {
    status: '',
    category: '',
  };

  const loadDashboard = async () => {
    setLoading(true);
    setError(null);
    try {
      const [sum, map, recents, pred] = await Promise.all([
        dashboardApi.getSummary(filters),
        dashboardApi.getMap(filters),
        complaintsApi.listMy().catch(() => []),
        predictionsApi.getSummary().catch(() => null)
      ]);
      setSummary(sum);
      setMapData(map);
      setRecentComplaints(recents.slice(0, 5));
      setPrediction(pred);
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, [filters]);



  if (loading && !summary) {
    return (
      <div className="flex flex-col items-center justify-center h-[60vh] space-y-4">
        <Loader2 className="h-10 w-10 text-civic-600 animate-spin" />
        <p className="text-gray-500 font-medium">Loading your civic dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-[60vh] space-y-4">
        <AlertTriangle className="h-12 w-12 text-red-500" />
        <h3 className="text-xl font-bold text-gray-900">Unable to load dashboard</h3>
        <p className="text-gray-500 max-w-md text-center">{error}</p>
        <Button onClick={loadDashboard} variant="outline" className="mt-4">Retry</Button>
      </div>
    );
  }

  if (!summary) return null;

  const resolvedCount = summary.status_counts.find(s => s.status === 'resolved')?.count || 0;
  const inProgressCount = summary.status_counts.find(s => s.status === 'in_progress')?.count || 0;
  const highPriorityCount = recentComplaints.filter(c => (c.priority_score || 0) >= 70).length;

  const topCategories = summary.category_counts.slice(0, 5);
  const othersCount = summary.category_counts.slice(5).reduce((acc, curr) => acc + curr.count, 0);
  
  const displayCategories = [...topCategories];
  if (othersCount > 0) {
    displayCategories.push({ category: 'others', count: othersCount });
  }

  let cumulativePercent = 0;
  const conicStops = displayCategories.map((c, i) => {
    const start = cumulativePercent;
    const size = summary.total_complaints > 0 ? (c.count / summary.total_complaints) * 100 : 0;
    cumulativePercent += size;
    return `${CATEGORY_COLORS[i % CATEGORY_COLORS.length]} ${start}% ${cumulativePercent}%`;
  }).join(', ');

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'resolved':
      case 'closed': return 'bg-green-100 text-green-700';
      case 'in_progress':
      case 'assigned': return 'bg-amber-100 text-amber-700';
      default: return 'bg-blue-100 text-blue-700';
    }
  };

  const getStatusDot = (status: string) => {
    switch (status) {
      case 'resolved':
      case 'closed': return 'bg-green-500';
      case 'in_progress':
      case 'assigned': return 'bg-amber-500';
      default: return 'bg-blue-500';
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-500 max-w-[1600px] mx-auto">
      {/* Header */}
      <div className="flex justify-between items-center bg-white px-2 py-4 mb-2">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            Good morning, {user?.display_name || 'Citizen'} <Hand className="h-6 w-6 text-yellow-500 animate-pulse" />
          </h1>
          <p className="text-slate-500 mt-1">Here is the status of your reported civic problems.</p>
        </div>
        <Button onClick={() => window.location.href = '/complaints/new'} className="bg-indigo-600 hover:bg-indigo-700">
          + Report a Problem
        </Button>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <Card className="border-0 shadow-sm rounded-xl">
          <CardContent className="p-5 flex items-center gap-4">
            <div className="h-12 w-12 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
              <FileText className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-slate-500">Total Reports</p>
              <p className="text-3xl font-bold text-slate-900">{summary.total_complaints}</p>
            </div>
          </CardContent>
        </Card>
        
        <Card className="border-0 shadow-sm rounded-xl">
          <CardContent className="p-5 flex items-center gap-4">
            <div className="h-12 w-12 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
              <CheckCircle2 className="h-6 w-6 text-green-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-slate-500">Resolved</p>
              <p className="text-3xl font-bold text-slate-900">{resolvedCount}</p>
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-sm rounded-xl">
          <CardContent className="p-5 flex items-center gap-4">
            <div className="h-12 w-12 rounded-full bg-amber-100 flex items-center justify-center flex-shrink-0">
              <Clock className="h-6 w-6 text-amber-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-slate-500">In Progress</p>
              <p className="text-3xl font-bold text-slate-900">{inProgressCount}</p>
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-sm rounded-xl">
          <CardContent className="p-5 flex items-center gap-4">
            <div className="h-12 w-12 rounded-full bg-purple-100 flex items-center justify-center flex-shrink-0">
              <FileText className="h-6 w-6 text-purple-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-slate-500">With Evidence</p>
              <p className="text-3xl font-bold text-slate-900">{summary.complaints_with_evidence}</p>
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-sm rounded-xl">
          <CardContent className="p-5 flex items-center gap-4">
            <div className="h-12 w-12 rounded-full bg-red-100 flex items-center justify-center flex-shrink-0">
              <AlertTriangle className="h-6 w-6 text-red-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-slate-500">High Priority</p>
              <p className="text-3xl font-bold text-slate-900">{highPriorityCount}</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Row 2: Overview, Breakdown, Map */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <Card className="border-0 shadow-sm rounded-xl lg:col-span-4">
          <CardHeader className="flex flex-row justify-between items-center pb-2">
            <CardTitle className="text-lg font-bold text-slate-800">My Reports Overview</CardTitle>
            <div className="text-xs font-medium text-slate-500 bg-slate-100 px-3 py-1 rounded-full cursor-pointer">This Month ⌄</div>
          </CardHeader>
          <CardContent className="flex items-center gap-8 pt-4">
            {summary.total_complaints > 0 ? (
              <>
                <div 
                  className="w-40 h-40 rounded-full flex items-center justify-center relative shadow-inner"
                  style={{ background: `conic-gradient(${conicStops})` }}
                >
                  <div className="w-28 h-28 bg-white rounded-full flex flex-col items-center justify-center absolute shadow-sm">
                    <span className="text-3xl font-bold text-slate-900">{summary.total_complaints}</span>
                    <span className="text-xs text-slate-500 font-medium">Total</span>
                  </div>
                </div>
                <div className="space-y-3 flex-1">
                  {displayCategories.map((c, i) => (
                    <div key={c.category} className="flex items-center justify-between text-sm">
                      <div className="flex items-center gap-2">
                        <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: CATEGORY_COLORS[i % CATEGORY_COLORS.length] }}></div>
                        <span className="text-slate-600 truncate max-w-[100px]" title={c.category.replace(/_/g, ' ')}>{c.category.replace(/_/g, ' ')}</span>
                      </div>
                      <div className="text-slate-900 font-medium">
                        {c.count} <span className="text-slate-400 font-normal text-xs ml-1">({((c.count / summary.total_complaints) * 100).toFixed(1)}%)</span>
                      </div>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div className="w-full flex flex-col items-center justify-center py-8">
                <BarChart3 className="h-10 w-10 text-slate-200 mb-2" />
                <p className="text-slate-500">No complaints available</p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="border-0 shadow-sm rounded-xl lg:col-span-3">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg font-bold text-slate-800">Status Breakdown</CardTitle>
          </CardHeader>
          <CardContent className="pt-4 space-y-4">
            {summary.status_counts.length > 0 ? summary.status_counts.map(s => (
              <div key={s.status} className="flex items-center justify-between p-3 rounded-lg bg-slate-50 border border-slate-100">
                <div className="flex items-center gap-3">
                  <div className={`w-2.5 h-2.5 rounded-full ${getStatusDot(s.status)}`}></div>
                  <span className="text-sm font-medium text-slate-700 capitalize">{s.status.replace(/_/g, ' ')}</span>
                </div>
                <span className="text-sm font-bold text-slate-900">{s.count}</span>
              </div>
            )) : (
              <div className="w-full flex flex-col items-center justify-center py-8 text-center">
                <p className="text-slate-500">No status data</p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="border-0 shadow-sm rounded-xl lg:col-span-5 flex flex-col">
          <CardHeader className="flex flex-row justify-between items-center pb-4">
            <CardTitle className="text-lg font-bold text-slate-800">Map of My Reports</CardTitle>
            <button onClick={() => setIsFullMapOpen(true)} className="text-sm text-indigo-600 font-medium hover:underline cursor-pointer focus:outline-none">View Full Map</button>
          </CardHeader>
          <CardContent className="flex-1 p-0 pb-6 px-6">
            <div className="h-full min-h-[220px] w-full rounded-xl overflow-hidden border border-slate-200 relative z-0">
              {mapData && mapData.features.length > 0 ? (
                <MapContainer 
                  center={[mapData.features[0].geometry.coordinates[1], mapData.features[0].geometry.coordinates[0]]} 
                  zoom={12} 
                  style={{ height: '100%', width: '100%' }}
                >
                  <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                  {mapData.features.map(f => (
                    <Marker key={f.properties.id} position={[f.geometry.coordinates[1], f.geometry.coordinates[0]]}>
                      <Popup>
                        <div className="text-sm space-y-1">
                          <p className="font-bold text-slate-900 leading-tight">{f.properties.title}</p>
                          <p className="text-xs text-slate-500 capitalize">{f.properties.category.replace(/_/g, ' ')}</p>
                        </div>
                      </Popup>
                    </Marker>
                  ))}
                </MapContainer>
              ) : (
                <div className="h-full w-full flex flex-col items-center justify-center bg-slate-50 text-slate-500">
                  <MapIcon className="h-8 w-8 text-slate-300 mb-2" />
                  <p className="text-sm">No location data available</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Row 3: Recent, AI Insights, Predictive */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <Card className="border-0 shadow-sm rounded-xl lg:col-span-4">
          <CardHeader className="flex flex-row justify-between items-center pb-2">
            <CardTitle className="text-lg font-bold text-slate-800">My Recent Reports</CardTitle>
            <a href="/complaints" className="text-sm text-indigo-600 font-medium hover:underline">View All</a>
          </CardHeader>
          <CardContent className="pt-2 divide-y divide-slate-100">
            {recentComplaints.length > 0 ? recentComplaints.map(c => (
              <div key={c.id} className="py-3 flex gap-4 items-start hover:bg-slate-50 rounded-lg transition-colors group cursor-pointer" onClick={() => window.location.href = `/complaints/${c.id}`}>
                <div className="h-12 w-12 rounded-lg bg-slate-100 border border-slate-200 overflow-hidden flex items-center justify-center flex-shrink-0">
                  <FileText className="h-5 w-5 text-slate-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-slate-900 truncate group-hover:text-indigo-600 transition-colors">{c.title}</p>
                  <p className="text-xs text-slate-500 capitalize truncate mt-0.5">{c.category.replace(/_/g, ' ')}</p>
                </div>
                <div className="text-right flex-shrink-0 flex flex-col items-end">
                  <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${getStatusColor(c.status)}`}>
                    {c.status.replace(/_/g, ' ')}
                  </span>
                  <span className="text-[10px] text-slate-400 mt-1">{new Date(c.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            )) : (
              <div className="py-8 text-center">
                <p className="text-sm text-slate-500">No complaints submitted yet.</p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="border-0 shadow-sm rounded-xl lg:col-span-4">
          <CardHeader className="flex flex-row justify-between items-center pb-2">
            <CardTitle className="text-lg font-bold text-slate-800">AI Insights</CardTitle>
            <a href="/intelligence" className="text-sm text-indigo-600 font-medium hover:underline">View All</a>
          </CardHeader>
          <CardContent className="pt-2 space-y-4">
            {prediction && prediction.status !== 'INSUFFICIENT_DATA' ? (
              <>
                <div className="p-4 rounded-xl border border-slate-100 bg-slate-50 flex items-center justify-between">
                  <div>
                    <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Top Issue This Month</p>
                    <p className="text-sm font-bold text-slate-900 capitalize">
                      {prediction.category_forecasts[0]?.category.replace(/_/g, ' ') || 'Various Issues'}
                    </p>
                    <p className="text-xs text-slate-500 mt-0.5">{prediction.category_forecasts[0]?.forecast_count || 0} expected complaints</p>
                  </div>
                  <Activity className="h-8 w-8 text-indigo-300" />
                </div>
                <div className="space-y-3">
                  <div className="flex gap-3 items-start">
                    <div className="p-2 rounded-lg bg-blue-50 text-blue-600 mt-0.5"><MapIcon className="h-4 w-4" /></div>
                    <div>
                      <p className="text-sm font-bold text-slate-900">Hotspot Area</p>
                      <p className="text-xs text-slate-500 leading-snug">
                        {prediction.hotspots.length > 0 ? `${prediction.hotspots.length} high-risk clusters identified` : 'No major hotspots identified.'}
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-3 items-start">
                    <div className="p-2 rounded-lg bg-red-50 text-red-600 mt-0.5"><Activity className="h-4 w-4" /></div>
                    <div>
                      <p className="text-sm font-bold text-slate-900">Trend Alert</p>
                      <p className="text-xs text-slate-500 leading-snug">
                        {prediction.overall_trend === 'INCREASING' ? 'Complaint volume is trending upwards.' : prediction.overall_trend === 'DECREASING' ? 'Complaint volume is trending downwards.' : 'Complaint volume is stable.'}
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-3 items-start">
                    <div className="p-2 rounded-lg bg-green-50 text-green-600 mt-0.5"><Clock className="h-4 w-4" /></div>
                    <div>
                      <p className="text-sm font-bold text-slate-900">Resolution Insight</p>
                      <p className="text-xs text-slate-500 leading-snug">Based on AI analysis of historical completion rates.</p>
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <div className="w-full flex flex-col items-center justify-center py-10 text-center">
                <Database className="h-8 w-8 text-slate-300 mb-3" />
                <p className="text-sm font-bold text-slate-900">No AI analyses available</p>
                <p className="text-xs text-slate-500 mt-1 max-w-[200px]">{prediction?.explanation || 'Insufficient historical data to generate reliable AI insights.'}</p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="border-0 shadow-sm rounded-xl lg:col-span-4 bg-gradient-to-br from-indigo-50 to-blue-50/30">
          <CardHeader className="flex flex-row justify-between items-center pb-2">
            <CardTitle className="text-lg font-bold text-slate-800">Predictive Insights</CardTitle>
            <a href="/intelligence" className="text-sm text-indigo-600 font-medium hover:underline">View Details</a>
          </CardHeader>
          <CardContent className="pt-2">
            {prediction && prediction.status !== 'INSUFFICIENT_DATA' ? (
              <div className="h-full flex flex-col justify-between">
                <div className="mb-6">
                  <p className="text-xs font-semibold text-indigo-500/80 uppercase tracking-wider mb-2">Next {prediction.forecast_horizon_days} Days Prediction</p>
                  <div className="flex justify-between items-start">
                    <p className="text-base font-semibold text-slate-800 leading-snug max-w-[220px]">
                      {prediction.explanation}
                    </p>
                    <CloudRain className="h-10 w-10 text-indigo-400 opacity-80" />
                  </div>
                </div>
                
                <div className="flex gap-4">
                  <div className="bg-white p-4 rounded-xl flex-1 shadow-sm border border-slate-100">
                    <p className="text-xs text-slate-500 mb-1">Risk Areas</p>
                    <p className="text-lg font-bold text-slate-900">{prediction.hotspots.length} areas identified</p>
                    <div className="mt-2 inline-flex items-center text-[10px] font-bold text-red-700 bg-red-100 px-2 py-0.5 rounded-full uppercase">
                      <AlertTriangle className="h-3 w-3 mr-1" /> High Risk
                    </div>
                  </div>
                  <div className="bg-white p-4 rounded-xl flex-1 shadow-sm border border-slate-100">
                    <p className="text-xs text-slate-500 mb-1">Expected Complaints</p>
                    <p className="text-lg font-bold text-slate-900">
                      {prediction.category_forecasts.reduce((acc, c) => acc + c.forecast_count, 0)} - {prediction.category_forecasts.reduce((acc, c) => acc + c.forecast_count, 0) + 15}
                    </p>
                    <div className="mt-2 text-indigo-500">
                      <BarChart3 className="h-4 w-4" />
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="h-full w-full flex flex-col items-center justify-center py-10 text-center">
                <Database className="h-8 w-8 text-indigo-200 mb-3" />
                <p className="text-sm font-bold text-slate-900">INSUFFICIENT_DATA</p>
                <p className="text-xs text-slate-500 mt-1 max-w-[200px]">Not enough historical reports to generate a reliable forecast.</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Row 4: How CivicPulse Works */}
      <Card className="border-0 shadow-sm rounded-xl overflow-hidden">
        <div className="bg-slate-50 p-6">
          <h3 className="text-base font-bold text-slate-800 mb-6">How CivicPulse AI Works</h3>
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 relative">
            <div className="absolute top-1/2 left-6 right-6 h-0.5 bg-slate-200 -z-10 hidden sm:block -translate-y-1/2"></div>
            
            <div className="flex flex-col items-center bg-slate-50 px-2">
              <div className="h-10 w-10 bg-white border-2 border-emerald-100 rounded-full flex items-center justify-center mb-3 shadow-sm text-emerald-600">
                <FileText className="h-5 w-5" />
              </div>
              <p className="text-sm font-bold text-slate-900 text-center">Report</p>
              <p className="text-xs text-slate-500 text-center">Submit a civic issue</p>
            </div>

            <div className="flex flex-col items-center bg-slate-50 px-2">
              <div className="h-10 w-10 bg-white border-2 border-blue-100 rounded-full flex items-center justify-center mb-3 shadow-sm text-blue-600">
                <Zap className="h-5 w-5" />
              </div>
              <p className="text-sm font-bold text-slate-900 text-center">AI Analysis</p>
              <p className="text-xs text-slate-500 text-center">Our AI analyzes the issue</p>
            </div>

            <div className="flex flex-col items-center bg-slate-50 px-2">
              <div className="h-10 w-10 bg-white border-2 border-purple-100 rounded-full flex items-center justify-center mb-3 shadow-sm text-purple-600">
                <Activity className="h-5 w-5" />
              </div>
              <p className="text-sm font-bold text-slate-900 text-center">Smart Routing</p>
              <p className="text-xs text-slate-500 text-center">Sent to relevant authority</p>
            </div>

            <div className="flex flex-col items-center bg-slate-50 px-2">
              <div className="h-10 w-10 bg-white border-2 border-amber-100 rounded-full flex items-center justify-center mb-3 shadow-sm text-amber-600">
                <ShieldCheck className="h-5 w-5" />
              </div>
              <p className="text-sm font-bold text-slate-900 text-center">Action</p>
              <p className="text-xs text-slate-500 text-center">Authority takes action</p>
            </div>

            <div className="flex flex-col items-center bg-slate-50 px-2">
              <div className="h-10 w-10 bg-white border-2 border-green-100 rounded-full flex items-center justify-center mb-3 shadow-sm text-green-600">
                <CheckCircle2 className="h-5 w-5" />
              </div>
              <p className="text-sm font-bold text-slate-900 text-center">You Track</p>
              <p className="text-xs text-slate-500 text-center">Track progress in real-time</p>
            </div>
          </div>
        </div>
      </Card>

      {/* Full Map Modal */}
      {isFullMapOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4 sm:p-6 lg:p-8">
          <div className="bg-white w-full h-full max-w-6xl max-h-[85vh] rounded-2xl shadow-2xl flex flex-col overflow-hidden animate-in zoom-in-95 duration-200 border border-slate-200">
            <div className="flex items-center justify-between p-4 border-b border-slate-100 bg-white shadow-sm z-10">
              <h2 className="text-lg font-bold text-slate-800 flex items-center gap-2">
                <MapIcon className="h-5 w-5 text-indigo-600" /> Full Complaints Map
              </h2>
              <button 
                onClick={() => setIsFullMapOpen(false)}
                className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500"
                aria-label="Close Map"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
              </button>
            </div>
            <div className="flex-1 w-full bg-slate-50 relative z-0">
              {mapData && mapData.features.length > 0 ? (
                <MapContainer 
                  center={[mapData.features[0].geometry.coordinates[1], mapData.features[0].geometry.coordinates[0]]} 
                  zoom={13} 
                  style={{ height: '100%', width: '100%', position: 'absolute', top: 0, left: 0 }}
                >
                  <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                  {mapData.features.map(f => (
                    <Marker key={f.properties.id} position={[f.geometry.coordinates[1], f.geometry.coordinates[0]]}>
                      <Popup>
                        <div className="text-sm space-y-1 min-w-[200px]">
                          <p className="font-bold text-slate-900 leading-tight">{f.properties.title}</p>
                          <p className="text-xs text-slate-500 capitalize">{f.properties.category.replace(/_/g, ' ')}</p>
                          <div className="pt-2 mt-2 border-t border-slate-100 flex items-center justify-between">
                            <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${getStatusColor(f.properties.status)}`}>
                              {f.properties.status.replace(/_/g, ' ')}
                            </span>
                            <a href={`/complaints/${f.properties.id}`} className="text-xs text-indigo-600 hover:underline">View Details &rarr;</a>
                          </div>
                        </div>
                      </Popup>
                    </Marker>
                  ))}
                </MapContainer>
              ) : (
                <div className="h-full w-full flex flex-col items-center justify-center text-slate-500">
                  <MapIcon className="h-12 w-12 text-slate-300 mb-3" />
                  <p className="font-medium text-slate-600">No location data available</p>
                  <p className="text-sm text-slate-400 mt-1">There are no complaints with location data to display on the map.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
