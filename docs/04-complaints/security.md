# Complaints Security Model

## Ownership Enforcement
A citizen can only interact with their own complaints. 
1. **Creation:** `user_id` is forcefully derived from the authenticated session inside `ComplaintService.create_complaint`. The `ComplaintCreateRequest` explicitly omits ownership and internal fields.
2. **Retrieval (`/my`):** The repository executes a database-level query (`find_many({"user_id": user_id})`). Ownership filtering is never deferred to the frontend or done in-memory.
3. **Details & History:** Accessing a specific complaint by ID validates `complaint["user_id"] == requesting_user_id`.

## Status & Field Manipulation Protection
- `ComplaintCreateRequest` only accepts `title`, `description`, `category`, and `location`.
- Attempting to inject `status`, `priority_score`, `department_id`, or timestamps via the API is rejected by Pydantic validation.
- Initial status is hardcoded to `SUBMITTED` by the backend.

## CSRF Analysis
Phase 3 uses HttpOnly cookie-based sessions, which inherently present a Cross-Site Request Forgery (CSRF) risk for state-changing requests like `POST /api/v1/complaints`.
- **Protection:** Our `civicpulse_session` cookie is configured with `SameSite=Lax`. In a modern browser environment, this prevents the cookie from being sent on cross-site `POST` requests.
- **CORS:** We use explicit, non-wildcard CORS origins, which protects `credentials: include` fetches from unauthorized domains.
- **Conclusion:** Standard SPA + `SameSite=Lax` + Explicit CORS provides sufficient CSRF protection for this MVP phase. If form-urlencoded cross-site POSTs become necessary, an explicit Anti-CSRF token header will be required.

## Data Exposure Prevention
- If a user requests a complaint ID belonging to another user, the API intentionally returns `404 Not Found` rather than `403 Forbidden` to prevent leaking the existence of other citizens' resources.
