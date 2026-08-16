/*
 * CivicPulse AI — Complaints API Methods.
 */

import { apiFetch } from './client';

export interface LocationData {
  geo: {
    type: 'Point';
    coordinates: [number, number]; // [longitude, latitude]
  };
  address?: string;
  locality?: string;
  city?: string;
  pincode?: string;
}

export interface ComplaintCreateRequest {
  title: string;
  description: string;
  category: string;
  location: LocationData;
}

export interface ComplaintResponse {
  id: string;
  user_id: string;
  title: string;
  description: string;
  category: string;
  location: LocationData;
  status: string;
  priority_score: number | null;
  department_id: string | null;
  cluster_id: string | null;
  evidence_count: number;
  created_at: string;
  updated_at: string;
}

export interface StatusHistoryResponse {
  id: string;
  complaint_id: string;
  previous_status: string | null;
  new_status: string;
  actor_id: string | null;
  reason: string | null;
  created_at: string;
}

export interface EvidenceResponse {
  id: string;
  complaint_id: string;
  user_id: string;
  original_filename: string;
  mime_type: string;
  size_bytes: number;
  processing_status: string;
  created_at: string;
}

export interface AIAnalysisResponse {
  id: string;
  complaint_id: string;
  provider: string;
  status: string;
  result: {
    category: string;
    summary: string;
    severity_indicators: string[];
    model_confidence: number;
  } | null;
  confidence: number | null;
  created_at: string;
  completed_at: string | null;
}

export const complaintsApi = {
  create: (data: ComplaintCreateRequest) => {
    return apiFetch<ComplaintResponse>('/api/v1/complaints/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  listMy: () => {
    return apiFetch<ComplaintResponse[]>('/api/v1/complaints/my', {
      method: 'GET',
    });
  },

  getById: (id: string) => {
    return apiFetch<ComplaintResponse>(`/api/v1/complaints/${id}`, {
      method: 'GET',
    });
  },

  getHistory: (id: string) => {
    return apiFetch<StatusHistoryResponse[]>(`/api/v1/complaints/${id}/history`, {
      method: 'GET',
    });
  },

  uploadEvidence: (complaintId: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiFetch<EvidenceResponse>(`/api/v1/complaints/${complaintId}/evidence`, {
      method: 'POST',
      body: formData,
    });
  },

  listEvidence: (complaintId: string) => {
    return apiFetch<EvidenceResponse[]>(`/api/v1/complaints/${complaintId}/evidence`, {
      method: 'GET',
    });
  },

  getAIAnalysis: (complaintId: string) => {
    return apiFetch<AIAnalysisResponse[]>(`/api/v1/complaints/${complaintId}/ai`, {
      method: 'GET',
    });
  },
};
