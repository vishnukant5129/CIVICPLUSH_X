"""
CivicPulse AI — Infrastructure Health Checks.

Provides real connectivity checks for infrastructure dependencies.

SECURITY:
- Connection URIs and credentials are NEVER included in check results.
- Only status/latency information is exposed.
"""

from __future__ import annotations

import time
from typing import Any, Dict

from app.database import mongodb, redis


async def check_mongodb() -> Dict[str, Any]:
    """
    Check MongoDB connectivity.

    Returns a dict with status and optional latency.
    Never includes connection URI or credentials.
    """
    start = time.monotonic()
    try:
        is_connected = await mongodb.check_connectivity()
        latency_ms = round((time.monotonic() - start) * 1000, 2)

        if is_connected:
            return {
                "status": "ok",
                "latency_ms": latency_ms,
            }
        else:
            return {
                "status": "unavailable",
                "detail": "MongoDB client not initialized or unreachable.",
            }
    except Exception as exc:
        return {
            "status": "error",
            "detail": f"MongoDB check failed: {type(exc).__name__}",
        }


async def check_redis() -> Dict[str, Any]:
    """
    Check Redis connectivity.

    Returns a dict with status and optional latency.
    Never includes connection URL or credentials.
    """
    start = time.monotonic()
    try:
        is_connected = await redis.check_connectivity()
        latency_ms = round((time.monotonic() - start) * 1000, 2)

        if is_connected:
            return {
                "status": "ok",
                "latency_ms": latency_ms,
            }
        else:
            return {
                "status": "unavailable",
                "detail": "Redis client not initialized or unreachable.",
            }
    except Exception as exc:
        return {
            "status": "error",
            "detail": f"Redis check failed: {type(exc).__name__}",
        }
