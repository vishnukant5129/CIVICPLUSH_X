# Security Audit

## 1. Authentication Architecture
- **Single System**: Session-based authentication using server-side Redis storage and random session keys.
- **Cookie Security**:
  - `HttpOnly`: True (prevents JavaScript token extraction and mitigates XSS risks).
  - `SameSite`: Lax (protects against cross-site request forgery).
  - `Secure`: Settable via settings for production HTTPS environments.
- **Session Lifespan**: Rolling window (default 7 days) managed in Redis.

## 2. Authorization & Scope Isolation
- **Role Enforcement**: Implemented in backend via `RoleChecker` dependency injection.
- **IDOR Protection**:
  - Complaints: Accessible to submitting citizen or authority/admin.
  - Evidence Download: Endpoint `/api/v1/authority/evidence/{id}/download` verifies complaint ownership for citizens and scope for authorities.
  - Path Traversal: Path normalization prevents directory traversal attacks (`../`).

## 3. Security Headers
- Added to all backend HTTP responses via `RequestIdMiddleware`:
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `X-XSS-Protection: 1; mode=block`
  - `Referrer-Policy: strict-origin-when-cross-origin`
