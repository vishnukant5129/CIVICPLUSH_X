"""
CivicPulse AI — MongoDB Connection Management.

Provides async MongoDB connectivity using PyMongo's async API.

SECURITY:
- Connection URIs are loaded from configuration, never hardcoded.
- URIs are never logged.

Lifecycle:
- connect() is called during application startup.
- close() is called during application shutdown.
- get_database() provides access to the configured database.
"""

from __future__ import annotations

import logging
from typing import Optional

from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

logger = logging.getLogger("civicpulse.database.mongodb")

# Module-level client — managed through connect/close lifecycle
_client: Optional[AsyncMongoClient] = None
_database: Optional[AsyncDatabase] = None


async def connect(uri: str, database_name: str) -> None:
    """
    Initialize the MongoDB async client and verify connectivity.

    Args:
        uri: MongoDB connection URI (from configuration).
        database_name: Target database name.

    Raises:
        ConnectionFailure: If the initial connection check fails.
    """
    global _client, _database

    if not uri:
        logger.warning(
            "MONGODB_URI is empty. MongoDB will not be available. "
            "Set MONGODB_URI in your environment to connect."
        )
        return

    logger.info("Connecting to MongoDB (database: %s)...", database_name)

    _client = AsyncMongoClient(
        uri,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
    )
    _database = _client[database_name]

    # Verify connectivity with a ping
    try:
        await _client.admin.command("ping")
        logger.info("MongoDB connection established successfully.")
    except (ConnectionFailure, ServerSelectionTimeoutError) as exc:
        logger.error("Failed to connect to MongoDB: %s", str(exc))
        _client = None
        _database = None
        raise


async def close() -> None:
    """Close the MongoDB client connection."""
    global _client, _database

    if _client is not None:
        logger.info("Closing MongoDB connection...")
        _client.close()
        _client = None
        _database = None
        logger.info("MongoDB connection closed.")


def get_database() -> Optional[AsyncDatabase]:
    """
    Get the current MongoDB database instance.

    Returns:
        The AsyncDatabase instance, or None if not connected.
    """
    return _database


def get_client() -> Optional[AsyncMongoClient]:
    """
    Get the current MongoDB client instance.

    Returns:
        The AsyncMongoClient instance, or None if not connected.
    """
    return _client


async def check_connectivity() -> bool:
    """
    Check if MongoDB is reachable.

    Returns:
        True if a ping succeeds, False otherwise.
    """
    if _client is None:
        return False
    try:
        await _client.admin.command("ping")
        return True
    except Exception:
        return False
