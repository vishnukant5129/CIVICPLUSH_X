"""
CivicPulse AI — Health and Readiness Endpoints.

GET /health — Lightweight liveness check. Is the process alive?
GET /ready  — Readiness check. Are infrastructure dependencies available?

SECURITY:
- No credentials or internal details are exposed.
- Safe for infrastructure monitoring / load balancers.
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.health.checks import check_mongodb, check_redis

router = APIRouter(tags=["Infrastructure"])


@router.get(
    "/health",
    summary="Liveness check",
    description="Returns 200 if the application process is alive.",
    response_description="Application is alive.",
)
async def health() -> JSONResponse:
    """Lightweight liveness probe."""
    return JSONResponse(
        status_code=200,
        content={"status": "ok"},
    )


@router.get(
    "/ready",
    summary="Readiness check",
    description=(
        "Checks whether the application is ready to serve requests "
        "by verifying infrastructure dependencies."
    ),
    response_description="Readiness status of all dependencies.",
)
async def ready() -> JSONResponse:
    """
    Readiness probe — checks MongoDB and Redis connectivity.

    Returns 200 if all dependencies are healthy.
    Returns 503 if any dependency is unavailable.
    """
    mongodb_status = await check_mongodb()
    redis_status = await check_redis()

    all_ok = (
        mongodb_status.get("status") == "ok"
        and redis_status.get("status") == "ok"
    )

    content = {
        "status": "ready" if all_ok else "not_ready",
        "dependencies": {
            "mongodb": mongodb_status,
            "redis": redis_status,
        },
    }

    return JSONResponse(
        status_code=200 if all_ok else 503,
        content=content,
    )
