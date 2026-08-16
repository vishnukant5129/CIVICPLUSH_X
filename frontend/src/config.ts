/**
 * CivicPulse AI — Centralized API Configuration.
 *
 * All backend API configuration is managed here.
 * No hardcoded URLs are scattered throughout components.
 *
 * SECURITY:
 * - No server-side secrets are exposed here.
 * - Only browser-safe configuration (public URLs).
 */

/**
 * Backend API base URL.
 *
 * Loaded from VITE_API_BASE_URL environment variable.
 * Falls back to localhost for development.
 *
 * Usage in .env:
 *   VITE_API_BASE_URL=http://localhost:8000
 *
 * In production:
 *   VITE_API_BASE_URL=https://api.civicpulse.example.com
 */
export const API_BASE_URL: string =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

/**
 * Google OAuth 2.0 Client ID.
 *
 * Public value — safe to expose in browser JavaScript.
 * The GOOGLE_CLIENT_SECRET is NEVER included here.
 *
 * Loaded from VITE_GOOGLE_CLIENT_ID environment variable.
 */
export const GOOGLE_CLIENT_ID: string =
  import.meta.env.VITE_GOOGLE_CLIENT_ID || "";

/**
 * Build a full API endpoint URL.
 *
 * @param path - API path (e.g., "/health", "/ready")
 * @returns Full URL (e.g., "http://localhost:8000/health")
 */
export function apiUrl(path: string): string {
  const base = API_BASE_URL.replace(/\/+$/, "");
  const cleanPath = path.startsWith("/") ? path : `/${path}`;
  return `${base}${cleanPath}`;
}
