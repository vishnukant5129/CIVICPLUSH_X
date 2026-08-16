"""
CivicPulse AI — FastAPI Application Entrypoint.

Application lifecycle:
    Startup:
        1. Load and validate configuration.
        2. Initialize structured logging.
        3. Connect to MongoDB.
        4. Ensure database indexes (idempotent).
        5. Connect to Redis.
        6. Register middleware.
        7. Register error handlers.
        8. Register routes.

    Shutdown:
        1. Close MongoDB connection.
        2. Close Redis connection.
        3. Exit cleanly.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.google_auth import router as google_auth_router
from app.api.complaints import router as complaints_router
from app.api.evidence import router as evidence_router
from app.api.dashboard import router as dashboard_router
from app.api.intelligence import router as intelligence_router
from app.api.authority import router as authority_router
from app.api.notifications import router as notifications_router
from app.api.predictions import router as predictions_router
from app.config import Settings, get_settings
from app.database import mongodb, redis
from app.database.init_db import ensure_indexes
from app.errors import register_error_handlers
from app.health.router import router as health_router
from app.logging_config import setup_logging
from app.middleware import RequestIdMiddleware

logger = logging.getLogger("civicpulse")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application startup and shutdown lifecycle.

    Startup: validate config, connect to infrastructure.
    Shutdown: release all resources cleanly.
    """
    settings: Settings = app.state.settings

    # --- Startup ---
    logger.info(
        "Starting %s (env=%s)...",
        settings.app_name,
        settings.app_env.value,
    )

    # Connect to MongoDB
    try:
        await mongodb.connect(
            uri=settings.mongodb_uri,
            database_name=settings.mongodb_database,
        )
        # Ensure indexes after successful connection
        db = mongodb.get_database()
        if db is not None:
            try:
                await ensure_indexes(db)
            except Exception as exc:
                logger.error("Index initialization failed: %s", str(exc))
    except Exception as exc:
        logger.error("MongoDB connection failed during startup: %s", str(exc))
        # Allow startup to continue — readiness endpoint will report unhealthy

    # Connect to Redis
    try:
        await redis.connect(url=settings.redis_url)
    except Exception as exc:
        logger.error("Redis connection failed during startup: %s", str(exc))
        # Allow startup to continue — readiness endpoint will report unhealthy

    logger.info("%s startup complete.", settings.app_name)

    yield

    # --- Shutdown ---
    logger.info("Shutting down %s...", settings.app_name)

    await mongodb.close()
    await redis.close()

    logger.info("%s shutdown complete.", settings.app_name)


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    This is the application factory. It:
    1. Loads and validates configuration.
    2. Creates the FastAPI instance with lifespan management.
    3. Registers middleware, error handlers, and routes.

    Returns:
        Configured FastAPI application instance.
    """
    # Load and validate configuration first
    settings = get_settings()

    # Initialize logging before anything else
    setup_logging(settings)

    # Create FastAPI app
    app = FastAPI(
        title=settings.app_name,
        description="AI-powered civic problem intelligence platform.",
        version="0.1.0",
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        lifespan=lifespan,
    )

    # Store settings on app state for access during lifespan
    app.state.settings = settings

    # --- Middleware ---
    # Request ID middleware (must be added before CORS)
    app.add_middleware(RequestIdMiddleware)

    # CORS middleware — origins from configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # --- Error Handlers ---
    register_error_handlers(app)

    # --- Routes ---
    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(google_auth_router)
    app.include_router(complaints_router)
    app.include_router(evidence_router)
    app.include_router(dashboard_router)
    app.include_router(intelligence_router)
    app.include_router(authority_router)
    app.include_router(notifications_router)
    app.include_router(predictions_router)

    return app


# Application instance used by uvicorn
app = create_app()
