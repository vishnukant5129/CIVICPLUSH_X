"""
CivicPulse AI — Health and Readiness Endpoint Tests.

Tests that:
- /health returns 200 with status ok.
- /ready returns dependency status.
- Error handling produces safe error responses.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio


@pytest.mark.asyncio
class TestHealthEndpoint:
    """Tests for GET /health."""

    async def test_health_returns_200(self, client):
        """Health endpoint should always return 200 if process is alive."""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    async def test_health_is_lightweight(self, client):
        """Health response should be minimal."""
        response = await client.get("/health")
        data = response.json()
        # Should not contain infrastructure details
        assert "dependencies" not in data
        assert "mongodb" not in data
        assert "redis" not in data


@pytest.mark.asyncio
class TestReadinessEndpoint:
    """Tests for GET /ready."""

    async def test_ready_returns_dependency_status(self, client):
        """Readiness endpoint should include dependency checks."""
        response = await client.get("/ready")
        data = response.json()
        assert "status" in data
        assert "dependencies" in data
        assert "mongodb" in data["dependencies"]
        assert "redis" in data["dependencies"]

    async def test_ready_returns_503_when_dependencies_unavailable(self, client):
        """When dependencies are down, readiness should return 503."""
        # With mocked (disconnected) dependencies, expect not_ready
        response = await client.get("/ready")
        # MongoDB and Redis are not actually connected in tests
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "not_ready"


@pytest.mark.asyncio
class TestErrorHandling:
    """Tests for global error handling."""

    async def test_404_returns_consistent_error(self, client):
        """Unknown routes should return consistent error format."""
        response = await client.get("/nonexistent-route")
        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "error"
        assert data["error"] == "http_error"

    async def test_error_response_contains_request_id(self, client):
        """Error responses should include request_id for tracing."""
        response = await client.get(
            "/nonexistent-route",
            headers={"X-Request-ID": "test-trace-123"},
        )
        data = response.json()
        assert data.get("request_id") == "test-trace-123"

    async def test_request_id_header_in_response(self, client):
        """Responses should include X-Request-ID header."""
        response = await client.get("/health")
        assert "X-Request-ID" in response.headers
        assert len(response.headers["X-Request-ID"]) > 0


@pytest.mark.asyncio
class TestSecurityChecks:
    """Verify no sensitive information is leaked."""

    async def test_health_no_credentials(self, client):
        """Health endpoint must not expose credentials."""
        response = await client.get("/health")
        body = response.text.lower()
        assert "password" not in body
        assert "secret" not in body
        assert "mongodb+srv" not in body
        assert "redis://" not in body

    async def test_ready_no_credentials(self, client):
        """Readiness endpoint must not expose credentials."""
        response = await client.get("/ready")
        body = response.text.lower()
        assert "password" not in body
        assert "secret" not in body
        assert "mongodb+srv" not in body
        assert "redis://" not in body
