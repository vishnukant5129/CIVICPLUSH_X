"""
CivicPulse AI — Structured Logging Configuration.

Provides consistent, structured logging across the application.

SECURITY:
- Secrets must NEVER be logged.
- Request bodies that may contain sensitive data must not be logged in full.
"""

from __future__ import annotations

import logging
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.config import Settings


def setup_logging(settings: "Settings") -> None:
    """
    Configure application-wide structured logging.

    Args:
        settings: Application settings containing log_level.
    """
    log_level = getattr(logging, settings.log_level, logging.INFO)

    # Define structured format
    if settings.is_development:
        # Human-readable format for development
        log_format = (
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
        )
    else:
        # Structured format for production/test — easier to parse
        log_format = (
            '{"timestamp":"%(asctime)s",'
            '"level":"%(levelname)s",'
            '"logger":"%(name)s",'
            '"message":"%(message)s"}'
        )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicates on reload
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(log_format))
    root_logger.addHandler(console_handler)

    # Silence noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("pymongo").setLevel(logging.WARNING)

    logger = logging.getLogger("civicpulse")
    logger.info(
        "Logging configured: level=%s, environment=%s",
        settings.log_level,
        settings.app_env.value,
    )
