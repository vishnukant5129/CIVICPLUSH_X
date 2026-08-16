"""
CivicPulse AI — Configuration Tests.

Tests that configuration validation works correctly:
- Default values are applied in development.
- Production requires MONGODB_URI.
- Debug mode is blocked in production.
- Log level validation works.
- CORS origins are parsed correctly.
"""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from app.config import Environment, Settings


class TestConfigDefaults:
    """Test default configuration values for development."""

    def test_default_environment_is_development(self, test_settings):
        assert test_settings.app_env == Environment.TEST

    def test_default_app_name(self, test_settings):
        assert test_settings.app_name == "CivicPulse AI"

    def test_default_debug_is_false(self, test_settings):
        assert test_settings.app_debug is False

    def test_default_backend_port(self, test_settings):
        assert test_settings.backend_port == 8000

    def test_default_mongodb_database(self, test_settings):
        assert test_settings.mongodb_database == "civicpulse"


class TestConfigValidation:
    """Test configuration validation rules."""

    def test_production_requires_mongodb_uri(self):
        """MONGODB_URI must be set in production."""
        with pytest.raises(Exception) as exc_info:
            Settings(
                app_env=Environment.PRODUCTION,
                mongodb_uri="",
            )
        assert "MONGODB_URI" in str(exc_info.value)

    def test_production_with_mongodb_uri_succeeds(self):
        """Production config with MONGODB_URI should work."""
        settings = Settings(
            app_env=Environment.PRODUCTION,
            mongodb_uri="mongodb+srv://test:test@cluster.example.net/",
        )
        assert settings.app_env == Environment.PRODUCTION
        assert settings.mongodb_uri != ""

    def test_debug_blocked_in_production(self):
        """APP_DEBUG=true must fail in production."""
        with pytest.raises(Exception) as exc_info:
            Settings(
                app_env=Environment.PRODUCTION,
                app_debug=True,
                mongodb_uri="mongodb+srv://test:test@cluster.example.net/",
            )
        assert "APP_DEBUG" in str(exc_info.value)

    def test_invalid_log_level_rejected(self):
        """Invalid log levels must be rejected."""
        with pytest.raises(Exception) as exc_info:
            Settings(log_level="INVALID")
        assert "LOG_LEVEL" in str(exc_info.value)

    def test_valid_log_levels_accepted(self):
        """Valid log levels should be accepted and normalized."""
        for level in ["debug", "INFO", "Warning", "ERROR", "critical"]:
            settings = Settings(log_level=level)
            assert settings.log_level == level.upper()


class TestConfigCors:
    """Test CORS origin parsing."""

    def test_single_origin(self):
        settings = Settings(cors_origins="http://localhost:5173")
        assert settings.cors_origin_list == ["http://localhost:5173"]

    def test_multiple_origins(self):
        settings = Settings(
            cors_origins="http://localhost:5173,https://app.example.com"
        )
        assert settings.cors_origin_list == [
            "http://localhost:5173",
            "https://app.example.com",
        ]

    def test_empty_origins(self):
        settings = Settings(cors_origins="")
        assert settings.cors_origin_list == []


class TestConfigEnvironmentProperties:
    """Test environment helper properties."""

    def test_is_development(self):
        settings = Settings(app_env=Environment.DEVELOPMENT)
        assert settings.is_development is True
        assert settings.is_production is False
        assert settings.is_test is False

    def test_is_production(self):
        settings = Settings(
            app_env=Environment.PRODUCTION,
            mongodb_uri="mongodb+srv://test:test@cluster.example.net/",
        )
        assert settings.is_production is True
        assert settings.is_development is False

    def test_is_test(self):
        settings = Settings(app_env=Environment.TEST)
        assert settings.is_test is True
        assert settings.is_production is False
