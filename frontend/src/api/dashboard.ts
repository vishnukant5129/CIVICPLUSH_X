import { apiFetch } from './client';

export interface StatusCount {
  status: string;
  count: number;
}

export interface CategoryCount {
  category: string;
  count: number;
}

export interface TrendPoint {
  date: string;
  count: number;
}

export interface DashboardSummaryResponse {
  total_complaints: number;
  status_counts: StatusCount[];
  category_counts: CategoryCount[];
  trend: TrendPoint[];
  complaints_with_evidence: number;
  ai_stats: { [key: string]: number };
}

export interface GeoJSONPoint {
  type: string;
  coordinates: number[];
}

export interface GeoJSONFeatureProperties {
  id: string;
  title: string;
  category: string;
  status: string;
  created_at: string;
}

export interface GeoJSONFeature {
  type: string;
  geometry: GeoJSONPoint;
  properties: GeoJSONFeatureProperties;
}

export interface GeoJSONFeatureCollection {
  type: string;
  features: GeoJSONFeature[];
}

export interface DashboardFilters {
  status?: string;
  category?: string;
  date_from?: string;
  date_to?: string;
}

export const dashboardApi = {
  getSummary: (filters: DashboardFilters = {}) => {
    const params = new URLSearchParams();
    if (filters.status) params.append('status', filters.status);
    if (filters.category) params.append('category', filters.category);
    if (filters.date_from) params.append('date_from', filters.date_from);
    if (filters.date_to) params.append('date_to', filters.date_to);

    const qs = params.toString() ? `?${params.toString()}` : '';
    return apiFetch<DashboardSummaryResponse>(`/api/v1/dashboard/summary${qs}`, {
      method: 'GET',
    });
  },

  getMap: (filters: DashboardFilters = {}) => {
    const params = new URLSearchParams();
    if (filters.status) params.append('status', filters.status);
    if (filters.category) params.append('category', filters.category);
    if (filters.date_from) params.append('date_from', filters.date_from);
    if (filters.date_to) params.append('date_to', filters.date_to);

    const qs = params.toString() ? `?${params.toString()}` : '';
    return apiFetch<GeoJSONFeatureCollection>(`/api/v1/dashboard/complaints/map${qs}`, {
      method: 'GET',
    });
  }
};
