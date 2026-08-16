/*
 * CivicPulse AI — Auth API Methods.
 */

import { apiFetch } from './client';

export type UserRole = 'citizen' | 'authority' | 'admin';

export interface User {
  id: string;
  email: string;
  display_name: string;
  role: UserRole;
  department_id?: string;
}

export const authApi = {
  login: (credentials: { email: string; password: string }) => {
    return apiFetch<User>('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  },

  register: (data: { email: string; display_name: string; password: string }) => {
    return apiFetch<User>('/api/v1/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  logout: () => {
    return apiFetch<void>('/api/v1/auth/logout', {
      method: 'POST',
    });
  },

  getMe: () => {
    return apiFetch<User>('/api/v1/auth/me', {
      method: 'GET',
    });
  },
};
