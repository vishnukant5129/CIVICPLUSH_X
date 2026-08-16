/*
 * CivicPulse AI — Frontend API Client.
 * 
 * A centralized fetch wrapper configured to include credentials
 * (cookies) automatically on cross-origin requests.
 */

import { API_BASE_URL } from '../config';

class APIError extends Error {
  public status: number;
  public data: any;

  constructor(status: number, message: string, data: any = null) {
    super(message);
    this.status = status;
    this.data = data;
    this.name = 'APIError';
  }
}

/**
 * Standard API fetch wrapper.
 * Automatically handles credentials (cookies) and JSON parsing.
 */
export async function apiFetch<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const headers = new Headers(options.headers || {});
  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(url, {
    ...options,
    headers,
    credentials: 'include', // Crucial for cookie-based session auth
  });

  // Handle 204 No Content
  if (response.status === 204) {
    return null as unknown as T;
  }

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    let message = data?.detail || response.statusText || 'API Request Failed';
    
    // Append specific field validation errors if they exist
    if (data?.error === 'validation_error' && Array.isArray(data?.errors)) {
      const fieldErrors = data.errors.map((e: any) => e.message).join(' | ');
      if (fieldErrors) {
        message = fieldErrors;
      }
    }

    throw new APIError(response.status, message, data);
  }

  return data as T;
}
