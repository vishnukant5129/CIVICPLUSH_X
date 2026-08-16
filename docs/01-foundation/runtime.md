# CivicPulse AI — Runtime Architecture

## Backend (FastAPI)

### Application Lifecycle

```
Startup
  ├── Load configuration (Pydantic Settings)
  ├── Validate configuration
  ├── Initialize structured logging
  ├── Connect to MongoDB (async)
  ├── Connect to Redis (async)
  ├── Register middleware (RequestID, CORS)
  ├── Register error handlers
  └── Register routes

Shutdown
  ├── Close MongoDB connection
  ├── Close Redis connection
  └── Exit cleanly
```

### Key Files

| File | Purpose |
|------|---------|
| `backend/app/main.py` | Application factory, lifespan management |
| `backend/app/config.py` | Centralized Pydantic Settings |
| `backend/app/logging_config.py` | Structured logging setup |
| `backend/app/errors.py` | Global error handling |
| `backend/app/middleware.py` | Request ID correlation |
| `backend/app/database/mongodb.py` | MongoDB async connection lifecycle |
| `backend/app/database/redis.py` | Redis async connection lifecycle |
| `backend/app/health/router.py` | Health and readiness endpoints |
| `backend/app/health/checks.py` | Infrastructure connectivity checks |

### API Endpoints (Phase 1)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Liveness check (is the process alive?) |
| GET | `/ready` | Readiness check (are dependencies available?) |
| GET | `/docs` | OpenAPI documentation (development only) |

### Error Response Format

All errors follow a consistent structure:

```json
{
  "status": "error",
  "error": "error_type",
  "detail": "Human-readable description",
  "request_id": "correlation-id"
}
```

### MongoDB Driver

Uses **PyMongo Async API** (modern async path). Motor is deprecated as of May 2026.

### Redis

Uses **redis-py** async (`redis.asyncio`).

## Frontend (React + Vite)

### Stack

- React 19 + TypeScript
- Vite build system
- Centralized API config in `frontend/src/config.ts`

### Key Files

| File | Purpose |
|------|---------|
| `frontend/src/config.ts` | Centralized API base URL configuration |
| `frontend/.env.example` | Browser-safe environment template |
