"""
CivicPulse AI — Database Connectivity Tests.

Tests MongoDB and Redis connectivity check behavior
WITHOUT connecting to real databases.

These tests verify:
- Health checks report correctly when disconnected.
- Health checks do not fabricate success.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.health.checks import check_mongodb, check_redis


@pytest.mark.asyncio
class TestMongoDBHealthCheck:
    """Test MongoDB connectivity check behavior."""

    async def test_reports_unavailable_when_no_client(self):
        """Should report unavailable when client is None."""
        with patch("app.database.mongodb._client", None):
            result = await check_mongodb()
            assert result["status"] == "unavailable"

    async def test_reports_ok_when_ping_succeeds(self):
        """Should report ok when ping succeeds."""
        mock_client = MagicMock()
        mock_client.admin.command = AsyncMock(return_value={"ok": 1})
        with patch("app.database.mongodb._client", mock_client):
            result = await check_mongodb()
            assert result["status"] == "ok"
            assert "latency_ms" in result

    async def test_reports_unavailable_when_ping_fails(self):
        """Should report unavailable when ping raises an exception."""
        mock_client = MagicMock()
        mock_client.admin.command = AsyncMock(side_effect=Exception("Connection refused"))
        with patch("app.database.mongodb._client", mock_client):
            result = await check_mongodb()
            # check_connectivity catches the exception and returns False
            assert result["status"] in ("unavailable", "error")


@pytest.mark.asyncio
class TestRedisHealthCheck:
    """Test Redis connectivity check behavior."""

    async def test_reports_unavailable_when_no_client(self):
        """Should report unavailable when client is None."""
        with patch("app.database.redis._client", None):
            result = await check_redis()
            assert result["status"] == "unavailable"

    async def test_reports_ok_when_ping_succeeds(self):
        """Should report ok when ping succeeds."""
        mock_client = AsyncMock()
        mock_client.ping = AsyncMock(return_value=True)
        with patch("app.database.redis._client", mock_client):
            result = await check_redis()
            assert result["status"] == "ok"
            assert "latency_ms" in result

    async def test_reports_unavailable_when_ping_fails(self):
        """Should report unavailable when ping raises."""
        mock_client = AsyncMock()
        mock_client.ping = AsyncMock(side_effect=Exception("Connection refused"))
        with patch("app.database.redis._client", mock_client):
            result = await check_redis()
            assert result["status"] in ("unavailable", "error")
