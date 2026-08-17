"""
CivicPulse AI — Centralized Application Configuration.

All application configuration is managed through this module using Pydantic
BaseSettings. Values are loaded from environment variables and .env files.

SECURITY:
- No secrets are hardcoded.
- No secret values are exposed in error messages.
- Configuration validation fails clearly when required values are missing.
"""

from __future__ import annotations

from enum import Enum
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Environment(str, Enum):
    """Supported application environments."""

    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TEST = "test"


class Settings(BaseSettings):
    """
    Central configuration for CivicPulse AI.

    All settings are loaded from environment variables. A .env file in the
    project root is automatically loaded when present.

    Required variables for production:
        MONGODB_URI — MongoDB connection string
        CORS_ORIGINS — Allowed CORS origins (comma-separated)
    """

    # --- Application ---
    app_env: Environment = Field(
        default=Environment.DEVELOPMENT,
        description="Application environment: development, production, or test.",
    )
    app_name: str = Field(
        default="CivicPulse AI",
        description="Application display name.",
    )
    app_debug: bool = Field(
        default=False,
        description="Enable debug mode. Must be False in production.",
    )

    # --- Backend Server ---
    backend_host: str = Field(
        default="0.0.0.0",
        description="Host to bind the backend server.",
    )
    backend_port: int = Field(
        default=8000,
        description="Port for the backend server.",
    )

    # --- Frontend ---
    frontend_url: str = Field(
        default="http://localhost:5173",
        description="URL of the frontend application (used for CORS, redirects).",
    )

    # --- MongoDB ---
    mongodb_uri: str = Field(
        default="",
        description="MongoDB connection URI. Required for production.",
    )
    mongodb_database: str = Field(
        default="civicpulse",
        description="MongoDB database name.",
    )

    # --- Redis ---
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL.",
    )

    # --- CORS ---
    cors_origins: str = Field(
        default="http://localhost:5173",
        description="Comma-separated list of allowed CORS origins.",
    )

    # --- Authentication / Sessions ---
    session_cookie_name: str = Field(
        default="civicpulse_session",
        description="Name of the session cookie.",
    )
    session_max_age_seconds: int = Field(
        default=86400 * 7,  # 7 days
        description="Session lifetime in seconds.",
    )
    civicpulse_bootstrap_admin_email: str = Field(
        default="arbab2171217@gmail.com",
        description="Email of the bootstrap super admin.",
    )

    # --- Google OAuth ---
    google_client_id: str = Field(
        default="",
        description="Google OAuth 2.0 Client ID. Required for Google Sign-In.",
    )
    google_client_secret: str = Field(
        default="",
        description="Google OAuth 2.0 Client Secret. NEVER expose to frontend.",
    )
    google_redirect_uri: str = Field(
        default="http://localhost:8000/api/v1/auth/google/callback",
        description="Google OAuth callback URI. Must match Google Cloud Console registration.",
    )
    ai_provider: str = Field(
        default="groq",
        description="AI Provider to use (e.g. groq).",
    )
    groq_api_key: str = Field(
        default="",
        description="API Key for Groq. Required if provider is groq.",
    )
    ai_model: str = Field(
        default="llama3-8b-8192",
        description="Model to use for AI analysis.",
    )

    # --- Storage Settings ---
    storage_path: str = Field(
        default="uploads",
        description="Local directory path for evidence storage (MVP).",
    )
    max_upload_size_bytes: int = Field(
        default=10 * 1024 * 1024, # 10MB
        description="Maximum allowed evidence upload size.",
    )

    # Intelligence / ML Settings
    embedding_provider: str = "sentence-transformers"
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_version: str = "v1"
    embedding_dimensions: int = 384
    
    candidate_search_limit: int = 50
    geo_candidate_radius_meters: float = 1000.0
    duplicate_similarity_threshold: float = 0.85
    related_similarity_threshold: float = 0.70
    temporal_proximity_days: int = 30
    
    clustering_algorithm: str = "connected_components"
    clustering_version: str = "v1"

    # Predictive Intelligence Settings (Phase 10)
    predictive_min_historical_complaints: int = 5
    predictive_min_category_complaints: int = 3
    predictive_forecast_horizon_days: int = 7
    predictive_grid_resolution_deg: float = 0.01
    predictive_min_hotspot_complaints: int = 2
    predictive_model_version: str = "v1.0-ewma-grid"

    # --- Logging ---
    log_level: str = Field(
        default="INFO",
        description="Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL.",
    )

    @field_validator("app_debug")
    @classmethod
    def debug_must_be_off_in_production(cls, v: bool, info) -> bool:
        """Prevent debug mode in production."""
        env = info.data.get("app_env")
        if env == Environment.PRODUCTION and v is True:
            raise ValueError(
                "APP_DEBUG must be False in production. "
                "Set APP_DEBUG=false or remove it."
            )
        return v

    @field_validator("mongodb_uri")
    @classmethod
    def validate_mongodb_uri(cls, v: str, info) -> str:
        """Validate MongoDB URI is provided in production."""
        env = info.data.get("app_env")
        if env == Environment.PRODUCTION and not v:
            raise ValueError(
                "MONGODB_URI is required in production. "
                "Set the MONGODB_URI environment variable to your MongoDB connection string."
            )
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Normalize and validate log level."""
        normalized = v.upper()
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if normalized not in valid_levels:
            raise ValueError(
                f"LOG_LEVEL must be one of {valid_levels}, got '{v}'."
            )
        return normalized

    @property
    def cors_origin_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        if not self.cors_origins:
            return []
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_development(self) -> bool:
        return self.app_env == Environment.DEVELOPMENT

    @property
    def is_production(self) -> bool:
        return self.app_env == Environment.PRODUCTION

    @property
    def is_test(self) -> bool:
        return self.app_env == Environment.TEST

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


def get_settings() -> Settings:
    """
    Create and validate application settings.

    Raises:
        ValidationError: If configuration is invalid. The error message
            will identify the problem without exposing secret values.
    """
    return Settings()
