# Complete REST API Inventory

## 1. Authentication (`/api/v1/auth`)
- `POST /register`: Registers a new user (`CITIZEN` by default). Returns user document.
- `POST /login`: Validates credentials and issues an HttpOnly session cookie in Redis.
- `POST /logout`: Invalidates session key in Redis and clears session cookie.
- `GET /me`: Returns current authenticated user profile.

## 2. Complaint Domain (`/api/v1/complaints`)
- `POST /`: Submits a citizen complaint with title, description, category, and geolocation.
- `GET /`: Lists complaints owned by the logged-in citizen (paginated).
- `GET /{complaint_id}`: Retrieves complaint detail for owner or authority.

## 3. Evidence Domain (`/api/v1/evidence`)
- `POST /upload`: Uploads image/PDF file evidence associated with a complaint.

## 4. Operational Authority & Admin (`/api/v1/authority`)
- `GET /dashboard/summary`: Aggregated operational metrics (status, category, departments).
- `GET /complaints`: Server-side filtered, sorted, and paginated complaint queue.
- `GET /complaints/{complaint_id}`: Enriched authority view with audit log, evidence, and status history.
- `POST /complaints/{complaint_id}/assign`: Assigns case to department and authority officer.
- `POST /complaints/{complaint_id}/status`: Transitions complaint lifecycle status with audit entry.
- `POST /complaints/{complaint_id}/route`: Triggers category and geospatial routing engine.
- `POST /complaints/{complaint_id}/external-delivery`: Triggers downstream municipal adapter delivery.
- `GET /evidence/{evidence_id}/download`: Secure file streaming endpoint with ownership check.
- `GET /departments`: Lists active municipal departments.

## 5. Predictive Intelligence (`/api/v1/predictions`)
- `GET /summary`: General volume forecasting summary and category trends.
- `GET /trends`: Trend direction breakdown across civic categories.
- `GET /hotspots`: Spatial hotspot risk scoring (Authority & Admin only).
- `POST /generate`: Triggers statistical predictive forecasting pipeline (Authority & Admin only).

## 6. Notifications (`/api/v1/notifications`)
- `GET /`: Lists user notifications with unread count.
- `POST /{id}/read`: Marks notification as read.
