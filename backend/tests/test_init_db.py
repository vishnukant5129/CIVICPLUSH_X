"""
CivicPulse AI — Database Initialization Tests.

Tests that:
- ensure_indexes runs without errors.
- Index creation calls are made for all collections.
- ensure_indexes is idempotent (safe to call multiple times).
- Collection names are consistent.

Uses mocked database — no real MongoDB connection.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest

from app.database.init_db import (
    COLLECTION_AI_ANALYSES,
    COLLECTION_ASSIGNMENTS,
    COLLECTION_AUDIT_LOGS,
    COLLECTION_COMPLAINTS,
    COLLECTION_DEPARTMENTS,
    COLLECTION_EVIDENCE,
    COLLECTION_INCIDENT_CLUSTERS,
    COLLECTION_NOTIFICATIONS,
    COLLECTION_PREDICTIONS,
    COLLECTION_STATUS_HISTORY,
    COLLECTION_USERS,
    ensure_indexes,
)


@pytest.fixture
def mock_db():
    """Create a mock AsyncDatabase with mock collections."""
    db = MagicMock()
    collections = {}

    def get_collection(name):
        if name not in collections:
            coll = AsyncMock()
            coll.create_index = AsyncMock(return_value="index_name")
            collections[name] = coll
        return collections[name]

    db.__getitem__ = MagicMock(side_effect=get_collection)
    db._collections = collections
    return db


class TestCollectionNames:
    """Test collection name constants are consistent."""

    def test_all_lowercase(self):
        names = [
            COLLECTION_USERS,
            COLLECTION_DEPARTMENTS,
            COLLECTION_COMPLAINTS,
            COLLECTION_EVIDENCE,
            COLLECTION_AI_ANALYSES,
            COLLECTION_INCIDENT_CLUSTERS,
            COLLECTION_ASSIGNMENTS,
            COLLECTION_STATUS_HISTORY,
            COLLECTION_NOTIFICATIONS,
            COLLECTION_PREDICTIONS,
            COLLECTION_AUDIT_LOGS,
        ]
        for name in names:
            assert name == name.lower(), f"Collection name '{name}' is not lowercase"

    def test_all_snake_case(self):
        names = [
            COLLECTION_USERS,
            COLLECTION_DEPARTMENTS,
            COLLECTION_COMPLAINTS,
            COLLECTION_EVIDENCE,
            COLLECTION_AI_ANALYSES,
            COLLECTION_INCIDENT_CLUSTERS,
            COLLECTION_ASSIGNMENTS,
            COLLECTION_STATUS_HISTORY,
            COLLECTION_NOTIFICATIONS,
            COLLECTION_PREDICTIONS,
            COLLECTION_AUDIT_LOGS,
        ]
        for name in names:
            assert " " not in name, f"Collection name '{name}' contains spaces"
            assert name.replace("_", "").isalpha(), f"Collection name '{name}' has unexpected chars"

    def test_expected_collection_names(self):
        assert COLLECTION_USERS == "users"
        assert COLLECTION_DEPARTMENTS == "departments"
        assert COLLECTION_COMPLAINTS == "complaints"
        assert COLLECTION_EVIDENCE == "evidence"
        assert COLLECTION_AI_ANALYSES == "ai_analyses"
        assert COLLECTION_INCIDENT_CLUSTERS == "incident_clusters"
        assert COLLECTION_ASSIGNMENTS == "assignments"
        assert COLLECTION_STATUS_HISTORY == "status_history"
        assert COLLECTION_NOTIFICATIONS == "notifications"
        assert COLLECTION_PREDICTIONS == "predictions"
        assert COLLECTION_AUDIT_LOGS == "audit_logs"


@pytest.mark.asyncio
class TestEnsureIndexes:
    """Test the ensure_indexes function."""

    async def test_runs_without_error(self, mock_db):
        """ensure_indexes should complete without raising."""
        await ensure_indexes(mock_db)

    async def test_creates_user_indexes(self, mock_db):
        await ensure_indexes(mock_db)
        coll = mock_db[COLLECTION_USERS]
        # Should have created at least the unique email index
        assert coll.create_index.call_count >= 2
        # Verify unique email index call
        calls = coll.create_index.call_args_list
        email_call = [c for c in calls if "idx_users_normalized_email_unique" in str(c)]
        assert len(email_call) == 1

    async def test_creates_complaint_geospatial_index(self, mock_db):
        await ensure_indexes(mock_db)
        coll = mock_db[COLLECTION_COMPLAINTS]
        calls = coll.create_index.call_args_list
        geo_call = [c for c in calls if "2dsphere" in str(c) or "GEOSPHERE" in str(c)]
        assert len(geo_call) >= 1

    async def test_creates_department_unique_code_index(self, mock_db):
        await ensure_indexes(mock_db)
        coll = mock_db[COLLECTION_DEPARTMENTS]
        calls = coll.create_index.call_args_list
        code_call = [c for c in calls if "idx_departments_code_unique" in str(c)]
        assert len(code_call) == 1

    async def test_creates_indexes_for_all_collections(self, mock_db):
        """All 11 collections should have indexes created."""
        await ensure_indexes(mock_db)
        expected_collections = [
            COLLECTION_USERS,
            COLLECTION_DEPARTMENTS,
            COLLECTION_COMPLAINTS,
            COLLECTION_EVIDENCE,
            COLLECTION_AI_ANALYSES,
            COLLECTION_INCIDENT_CLUSTERS,
            COLLECTION_ASSIGNMENTS,
            COLLECTION_STATUS_HISTORY,
            COLLECTION_NOTIFICATIONS,
            COLLECTION_PREDICTIONS,
            COLLECTION_AUDIT_LOGS,
        ]
        accessed = [str(c) for c in mock_db.__getitem__.call_args_list]
        for coll_name in expected_collections:
            assert any(coll_name in a for a in accessed), \
                f"No indexes created for collection '{coll_name}'"

    async def test_idempotent_second_call(self, mock_db):
        """Calling ensure_indexes twice should not raise."""
        await ensure_indexes(mock_db)
        await ensure_indexes(mock_db)
        # Should succeed both times without error
