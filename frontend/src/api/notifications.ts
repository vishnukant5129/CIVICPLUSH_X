import { apiFetch } from './client';

export interface NotificationItem {
  id: string;
  user_id: string;
  event_id?: string;
  complaint_id?: string;
  type: string;
  title: string;
  body: string;
  read: boolean;
  read_at?: string;
  created_at: string;
  metadata?: Record<string, any>;
}

export interface NotificationPreferences {
  user_id: string;
  in_app_enabled: boolean;
  email_enabled: boolean;
  sms_enabled: boolean;
  push_enabled: boolean;
  updated_at: string;
}

export const notificationsApi = {
  getNotifications: async (unreadOnly = false, skip = 0, limit = 20): Promise<NotificationItem[]> => {
    const query = new URLSearchParams({
      unread_only: String(unreadOnly),
      skip: String(skip),
      limit: String(limit),
    });
    return apiFetch<NotificationItem[]>(`/api/v1/notifications?${query.toString()}`);
  },

  getUnreadCount: async (): Promise<number> => {
    const res = await apiFetch<{ unread_count: number }>('/api/v1/notifications/unread-count');
    return res.unread_count;
  },

  markAsRead: async (notificationId: string): Promise<void> => {
    await apiFetch(`/api/v1/notifications/${notificationId}/read`, {
      method: 'PATCH',
    });
  },

  markAllAsRead: async (): Promise<{ marked_count: number }> => {
    return apiFetch<{ marked_count: number }>('/api/v1/notifications/mark-all-read', {
      method: 'POST',
    });
  },

  getPreferences: async (): Promise<NotificationPreferences> => {
    return apiFetch<NotificationPreferences>('/api/v1/notifications/preferences');
  },

  updatePreferences: async (payload: Partial<NotificationPreferences>): Promise<NotificationPreferences> => {
    return apiFetch<NotificationPreferences>('/api/v1/notifications/preferences', {
      method: 'PUT',
      body: JSON.stringify(payload),
    });
  },
};
