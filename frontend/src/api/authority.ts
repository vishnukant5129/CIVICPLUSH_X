import { apiFetch } from './client';

export interface AuthorityDashboardSummary {
  total_complaints: number;
  unassigned_count: number;
  assigned_to_me_count: number;
  in_progress_count: number;
  resolved_count: number;
  closed_count: number;
  status_counts: Array<{ status: string; count: number }>;
  category_counts: Array<{ category: string; count: number }>;
  recent_audit_activity: Array<any>;
  integration_status: Record<string, number>;
  scope_note: string;
}

export interface AuthorityComplaintItem {
  _id: string;
  title: string;
  description: string;
  category: string;
  status: string;
  created_at: string;
  updated_at?: string;
  user_id: string;
  evidence_count: number;
  assigned_authority_id?: string;
  department_id?: string;
  priority_score?: number;
}

export interface AuthorityQueueResponse {
  items: AuthorityComplaintItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface AuthorityComplaintDetail {
  complaint: AuthorityComplaintItem;
  evidence: Array<any>;
  ai_analysis: Array<any>;
  assignment?: any;
  status_history: Array<any>;
  audit_trail: Array<any>;
  routing_info?: any;
  intelligence?: any;
  external_delivery?: any;
}

export interface QueueFilters {
  status?: string;
  category?: string;
  assignment?: string;
  search?: string;
  sort_by?: string;
  sort_order?: string;
  page?: number;
  page_size?: number;
}

export const authorityApi = {
  getSummary: async (): Promise<AuthorityDashboardSummary> => {
    return apiFetch<AuthorityDashboardSummary>('/api/v1/authority/dashboard/summary');
  },

  getComplaintQueue: async (filters: QueueFilters = {}): Promise<AuthorityQueueResponse> => {
    const params = new URLSearchParams();
    if (filters.status) params.append('status', filters.status);
    if (filters.category) params.append('category', filters.category);
    if (filters.assignment) params.append('assignment', filters.assignment);
    if (filters.search) params.append('search', filters.search);
    if (filters.sort_by) params.append('sort_by', filters.sort_by);
    if (filters.sort_order) params.append('sort_order', filters.sort_order);
    if (filters.page) params.append('page', filters.page.toString());
    if (filters.page_size) params.append('page_size', filters.page_size.toString());

    const queryString = params.toString();
    const url = `/api/v1/authority/complaints${queryString ? `?${queryString}` : ''}`;
    return apiFetch<AuthorityQueueResponse>(url);
  },

  getComplaintDetail: async (complaintId: string): Promise<AuthorityComplaintDetail> => {
    return apiFetch<AuthorityComplaintDetail>(`/api/v1/authority/complaints/${complaintId}`);
  },

  assignComplaint: async (complaintId: string, departmentId: string, authorityId: string) => {
    return apiFetch<{ status: string; message: string }>(`/api/v1/authority/complaints/${complaintId}/assign`, {
      method: 'POST',
      body: JSON.stringify({ department_id: departmentId, authority_id: authorityId }),
    });
  },

  updateStatus: async (complaintId: string, newStatus: string, note?: string) => {
    return apiFetch<{ status: string; message: string }>(`/api/v1/authority/complaints/${complaintId}/status`, {
      method: 'POST',
      body: JSON.stringify({ new_status: newStatus, note }),
    });
  },

  triggerRoute: async (complaintId: string) => {
    return apiFetch<any>(`/api/v1/authority/complaints/${complaintId}/route`, {
      method: 'POST',
    });
  },

  triggerExternalDelivery: async (complaintId: string) => {
    return apiFetch<any>(`/api/v1/authority/complaints/${complaintId}/external-delivery`, {
      method: 'POST',
    });
  },

  listDepartments: async (): Promise<Array<{ id: string; department_id: string; name: string }>> => {
    return apiFetch<Array<{ id: string; department_id: string; name: string }>>('/api/v1/authority/departments');
  },
};
