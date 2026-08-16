## [1.3.0] - 2026-08-16

### Phase 13 — Unified Docker Stack & Safe Repository Cleanup

#### Added
- **Unified Docker Stack:** Orchestrated 4-container Docker stack (`frontend`, `backend`, `mongodb`, `redis`) runnable with `docker compose up --build`.
- **Data Persistence:** Integrated named volumes `mongodb_data`, `redis_data`, and `uploads_data` to safeguard complaints, session keys, and uploaded evidence across container restarts.
- **Root Documentation & Cleanup:** Added unified root `README.md` and repository cleanup manifest under `docs/13-docker-cleanup/cleanup-manifest.md`.

## [1.2.0] - 2026-08-16

### Phase 12 — Final Production Hardening, Security Audit, Integration Verification & End-to-End Validation

#### Added
- **Security Headers:** Enforced `X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`, and `Referrer-Policy` across all API responses.
- **Production Readiness Documentation Suite:** Generated 13 audit documents under `docs/12-production-readiness/` covering architecture, security, authorization, reliability, data integrity, and deployment.
- **Verification:** Full suite regression verified with 144 unit/integration tests passing and clean production frontend build.

## [1.1.0] - 2026-08-16

### Phase 11 — Authority & Admin Operations Dashboard

#### Added
- **Operational Queue API:** Added `GET /api/v1/authority/complaints` with server-side pagination, search, status filtering, category filtering, and scope options.
- **Operational Metrics:** Added `GET /api/v1/authority/dashboard/summary` returning real-time status and department distributions.
- **Enriched Case Detail:** Added `GET /api/v1/authority/complaints/{id}` embedding evidence, AI analysis, status history, and immutable audit logs.
- **Protected Evidence Streaming:** Added `GET /api/v1/authority/evidence/{id}/download` enforcing role and ownership authorization.
- **Frontend Dashboard:** Implemented `AuthorityDashboard.tsx` with case inspection, assignment controls, and predictive intelligence suite.

## [0.8.0] - 2026-08-16

### Phase 8 — Authority Operations & Routing

#### Added
- **Authority Domain & Audit Trail:** Implemented strict, immutable `AuthorityActionHistory` logs for all domain-level updates (`ASSIGNED`, `STATUS_UPDATE`) guaranteeing append-only historical records for administrative accountability.
- **Data-Driven Routing Engine:** Engineered `RoutingService` to process complaints through dynamically modeled `RoutingRule` schemas rather than brittle Python logic limits. Emits secure assignment allocations explicitly separated from hallucinated API calls.
- **Status State Machine:** Confined workflow operations directly to explicit paths (e.g. `SUBMITTED` -> `ASSIGNED` -> `IN_PROGRESS` -> `RESOLVED`) guarding against malicious jumps to unverified stages.
- **External Integration Abstraction:** Shipped an honest boundary interface (`GovernmentIntegrationAdapter`). Successfully blocked CivicPulse from faking delivery responses; gracefully returns `NOT_CONFIGURED` without polluting databases with fake ticket metrics.

## [0.5.0] - 2026-08-16

### Phase 5 — Evidence Intelligence + AI Understanding

#### Added
- **Geolocation:** Refactored `ComplaintForm` to use real browser `navigator.geolocation` instead of simulated hardcoded coordinates.
- **Evidence Storage:** Implemented secure local storage (`uploads/`) with UUID filenames to prevent path traversal. Restricted to `.jpg, .png, .webp, .pdf` up to 10MB.
- **AI Integration:** Integrated `groq` SDK for fast asynchronous LLM analysis on newly uploaded evidence.
- **Structured AI:** Forced the model to output strict JSON metadata (category, summary, severity indicators, confidence) validated against Python domain logic.
- **API Endpoints:** Created `/api/v1/complaints/{id}/evidence` and `/api/v1/complaints/{id}/ai` routes.
- **Frontend App:** Added an Evidence upload section and an AI status tracker card within `ComplaintDetail.tsx`.
- **Documentation:** Phase 5 domain and security model documentation (`docs/05-ai/`).

## [0.4.0] - 2026-08-16

### Phase 4 — Citizen Complaint Domain

#### Added
- **API Models:** `ComplaintCreateRequest`, `ComplaintResponse`, `StatusHistoryResponse` ensuring frontend data safety.
- **Service Layer:** `ComplaintService` coordinating persistence, status history creation, and ownership verification.
- **API Routes:** `POST /api/v1/complaints/`, `GET /api/v1/complaints/my`, `GET /api/v1/complaints/{id}`, `GET /api/v1/complaints/{id}/history`.
- **Security:** Strict server-side ownership. Unknown internal fields are ignored; status and IDs are forced by the backend. Out-of-bounds cross-user requests return 404 to avoid enumeration.
- **Frontend App:** Fully functional React router implementation (`App.tsx`).
- **Frontend Components:** `ComplaintForm.tsx`, `MyComplaints.tsx`, `ComplaintDetail.tsx` providing real, API-backed state without fake data.
- **Documentation:** Phase 4 domain and security model documentation (`docs/04-complaints/`).

## [0.3.0] - 2026-08-16

### Phase 3 — Production-Grade Authentication, Identity & Authorization

#### Added
- **Dependencies:** `passlib[bcrypt]` for secure password hashing.
- **Sessions:** Redis-backed sessions with 32-byte opaque URL-safe tokens.
- **Cookies:** `civicpulse_session` configured with `HttpOnly`, `SameSite=Lax`, and `Secure` (in prod).
- **Domain:** Upgraded `UserDocument` to include `password_hash`.
- **API Models:** Created `RegisterRequest`, `LoginRequest`, `UserResponse`.
- **Auth Routes:** `POST /api/v1/auth/register`, `/login`, `/logout`, and `GET /me`.
- **Backend Authorization:** Dependencies `require_authenticated_user` and `RoleChecker`.
- **Security:** Forced `CITIZEN` role on registration; login returns generic generic 401s to prevent enumeration.
- **Frontend State:** `AuthContext` established.
- **Frontend Client:** Centralized `apiFetch` ensuring cross-origin requests always include credentials.
- **Frontend Routes:** Protected route wrapper `ProtectedRoute` foundation.
- **Documentation:** Phase 3 security and auth architecture documentation (`docs/03-auth/`).

## [0.2.0] - 2026-08-16

### Phase 2 — Database Architecture, Domain Models, Repositories & Core Backend Foundation

#### Added
- **Domain Enums:** Centralized enums for roles, statuses, and categories (`backend/app/domain/enums.py`).
- **Domain Schemas:** Pydantic schemas for 11 core domain objects (`backend/app/domain/schemas.py`).
- **Validation:** Enforced GeoJSON boundaries, email format, size constraints, and valid transitions.
- **Database Init:** Idempotent `ensure_indexes` process added to application startup (`backend/app/database/init_db.py`).
- **Indexes:** Defined unique, geospatial (2dsphere), and compound indexes for all collections.
- **Repository Base:** Reusable async MongoDB repository primitives (`backend/app/repositories/base.py`).
- **Repositories:** Collection-specific repositories with domain queries (`backend/app/repositories/collections.py`).
- **Error Handling:** Repository errors translated from PyMongo exceptions.
- **Tests:** 78 new tests covering schemas, enums, repositories, and database init.
- **Documentation:** Phase 2 database docs (`docs/02-database/`).

#### Design Decisions
- **Embedded Location:** `LocationData` and `GeoJSONPoint` embedded inside complaints.
- **Referenced Data:** Evidence, AI analysis, and status history stored in separate collections.
- **Application Enums:** `CivicCategory` managed in code, not database.
- **ObjectId Serialization:** `_id` converted to `id` by repository layer.

## [0.1.0] - 2026-08-16

### Phase 1 — Foundation, Environment, Configuration, Runtime & Observability

#### Added
- **Repository:** Git initialization, `.gitignore`
- **Configuration:** Centralized Pydantic Settings (`backend/app/config.py`)
- **Configuration:** `.env.example` with safe placeholders (root and frontend)
- **Configuration:** Environment validation (production requires MONGODB_URI, blocks debug)
- **Configuration:** Environment model: development / test / production
- **Backend:** FastAPI application factory with lifecycle management (`backend/app/main.py`)
- **Backend:** Structured logging with dev/prod formats (`backend/app/logging_config.py`)
- **Backend:** Global error handling — consistent safe responses (`backend/app/errors.py`)
- **Backend:** Request ID middleware for correlation (`backend/app/middleware.py`)
- **Backend:** CORS middleware — configuration-driven origins
- **Database:** MongoDB async connection manager using PyMongo async (`backend/app/database/mongodb.py`)
- **Database:** Redis async connection manager using redis-py (`backend/app/database/redis.py`)
- **Health:** `GET /health` — lightweight liveness check
- **Health:** `GET /ready` — readiness check with real MongoDB/Redis connectivity verification
- **Health:** Infrastructure health checks with real ping commands (`backend/app/health/checks.py`)
- **Frontend:** React + Vite + TypeScript scaffold
- **Frontend:** Centralized API configuration (`frontend/src/config.ts`)
- **Docker:** Docker Compose with backend, frontend, Redis services
- **Docker:** Real healthchecks for backend and Redis
- **Docker:** Backend Dockerfile with health check
- **Docker:** Frontend Dockerfile for development
- **Tests:** pytest + pytest-asyncio test foundation (31 tests)
- **Tests:** Configuration validation tests (16 tests)
- **Tests:** Health/readiness endpoint tests (8 tests)
- **Tests:** Database connectivity check tests (7 tests)
- **Documentation:** Phase 1 foundation docs (`docs/01-foundation/`)

#### Design Decisions
- **MongoDB driver:** PyMongo Async (not Motor, which is deprecated as of May 2026)
- **No local MongoDB container:** Atlas is the target per MASTER_PLAN.md
- **Redis included:** Required by planned RQ background processing architecture
- **No domain collections:** Phase 1 establishes connectivity only
