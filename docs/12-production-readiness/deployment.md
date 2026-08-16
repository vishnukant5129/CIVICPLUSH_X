# Deployment Readiness & Docker Infrastructure

## 1. Containerization Architecture
CivicPulse AI features containerization via `docker-compose.yml`:
- **`backend`**: FastAPI application container (Python 3.12-slim) with health checks pointing to `http://localhost:8000/health`.
- **`frontend`**: Vite React container served via Nginx on port 5173.
- **`redis`**: Alpine Redis 7 container with health checks (`redis-cli ping`) and persistent volume `redis_data`.
- **`mongodb`**: External or containerized MongoDB database with 2dsphere indexing support.

## 2. Health & Readiness Checks
- `GET /health`: Returns application status, database connectivity status, Redis status, environment name, and uptime.
- `GET /health/liveness`: Returns HTTP 200 `{"status": "live"}` for container orchestrators (Kubernetes / Docker Compose).
- `GET /health/readiness`: Returns HTTP 200 if MongoDB & Redis connections are active, or HTTP 503 if infrastructure is unreachable.
