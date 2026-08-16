import { apiFetch } from './client';

export interface ComplaintRelation {
  id: string;
  complaint_a_id: string;
  complaint_b_id: string;
  relation_type: 'duplicate' | 'related' | 'independent' | 'insufficient_data';
  semantic_similarity: number;
  geographic_distance_meters: number | null;
  category_match: boolean;
  temporal_distance_days: number;
  match_score: number;
  explanation: string;
  created_at: string;
}

export interface IncidentCluster {
  id: string;
  cluster_id: string;
  member_complaint_ids: string[];
  clustering_algorithm: string;
  created_at: string;
  updated_at: string;
}

export interface IntelligenceResponse {
  complaint_id: string;
  relations: ComplaintRelation[];
  cluster: IncidentCluster | null;
}

export const intelligenceApi = {
  getForComplaint: (complaintId: string) => {
    return apiFetch<IntelligenceResponse>(`/api/v1/intelligence/complaints/${complaintId}`, {
      method: 'GET',
    });
  },
  
  processComplaint: (complaintId: string) => {
    return apiFetch<{ status: string; message: string }>(`/api/v1/intelligence/complaints/${complaintId}/process`, {
      method: 'POST',
    });
  }
};
