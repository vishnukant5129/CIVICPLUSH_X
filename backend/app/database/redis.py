"""
CivicPulse AI — Redis Connection Management.

Provides async Redis connectivity for background processing infrastructure.

SECURITY:
- Connection URLs are loaded from configuration, never hardcoded.
- URLs are never logged.

Lifecycle:
- connect() is called during application startup.
- close() is called during application shutdown.
"""

from __future__ import annotations

import logging
from typing import Optional

import redis.asyncio as aioredis
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import TimeoutError as RedisTimeoutError

logger = logging.getLogger("civicpulse.database.redis")

# Module-level client — managed through connect/close lifecycle
_client: Optional[aioredis.Redis] = None


async def connect(url: str) -> None:
    """
    Initialize the Redis async client and verify connectivity.

    Args:
        url: Redis connection URL (from configuration).

    Raises:
        RedisConnectionError: If the initial connection check fails.
    """
    global _client

    if not url:
        logger.warning(
            "REDIS_URL is empty. Redis will not be available. "
            "Set REDIS_URL in your environment to connect."
        )
        return

    logger.info("Connecting to Redis...")

    _client = aioredis.from_url(
        url,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
    )

    # Verify connectivity with a ping
    try:
        await _client.ping()
        logger.info("Redis connection established successfully.")
    except (RedisConnectionError, RedisTimeoutError, OSError) as exc:
        logger.error("Failed to connect to Redis: %s", str(exc))
        _client = None
        raise


async def close() -> None:
    """Close the Redis client connection."""
    global _client

    if _client is not None:
        logger.info("Closing Redis connection...")
        await _client.close()
        _client = None
        logger.info("Redis connection closed.")


def get_client() -> Optional[aioredis.Redis]:
    """
    Get the current Redis client instance.

    Returns:
        The Redis client instance, or None if not connected.
    """
    return _client


async def check_connectivity() -> bool:
    """
    Check if Redis is reachable.

    Returns:
        True if a ping succeeds, False otherwise.
    """
    if _client is None:
        return False
    try:
        await _client.ping()
        return True
    except Exception:
        return False
