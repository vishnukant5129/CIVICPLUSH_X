"""
CivicPulse AI — Test Configuration and Fixtures.

All tests use APP_ENV=test to ensure complete isolation from
development and production environments.

No test connects to production databases.
"""

from __future__ import annotations

import os
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# Set test environment BEFORE importing application code
os.environ["APP_ENV"] = "test"
os.environ["MONGODB_URI"] = ""
os.environ["REDIS_URL"] = ""
os.environ["CORS_ORIGINS"] = "http://localhost:5173"
os.environ["LOG_LEVEL"] = "WARNING"


@pytest.fixture
def test_settings():
    """Provide test settings instance."""
    from app.config import get_settings
    return get_settings()


@pytest_asyncio.fixture
async def client():
    """
    Provide an async test client for the FastAPI application.

    MongoDB and Redis connections are mocked to prevent any external
    dependency during unit tests.
    """
    with patch("app.main.mongodb") as mock_mongo, \
         patch("app.main.redis") as mock_redis:
        mock_mongo.connect = AsyncMock()
        mock_mongo.close = AsyncMock()
        mock_redis.connect = AsyncMock()
        mock_redis.close = AsyncMock()

        from app.main import create_app
        app = create_app()

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
            yield ac
