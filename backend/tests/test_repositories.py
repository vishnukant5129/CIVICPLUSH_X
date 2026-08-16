"""
CivicPulse AI — Repository Layer Tests.

Tests base repository CRUD operations, pagination, error handling,
and ID serialization using mocked MongoDB collections.

No real database connection. All MongoDB calls are mocked.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from bson import ObjectId

from app.repositories.base import (
    BaseRepository,
    DocumentNotFoundError,
    DuplicateDocumentError,
    InvalidIdError,
    RepositoryError,
    _serialize_doc,
    _to_object_id,
)


# --- Helper: concrete repository for testing ---

class _ConcreteRepo(BaseRepository):
    collection_name = "test_collection"


# --- Fixtures ---

@pytest.fixture
def mock_db():
    """Create a mock AsyncDatabase."""
    db = MagicMock()
    collection = AsyncMock()
    db.__getitem__ = MagicMock(return_value=collection)
    return db


@pytest.fixture
def repo(mock_db):
    """Create a TestCollectionRepo with mocked DB."""
    return _ConcreteRepo(mock_db)


# === Unit tests ===

class TestIdSerialization:
    """Test _id → id conversion."""

    def test_serialize_doc_converts_id(self):
        oid = ObjectId()
        doc = {"_id": oid, "name": "test"}
        result = _serialize_doc(doc)
        assert "id" in result
        assert "_id" not in result
        assert result["id"] == str(oid)
        assert result["name"] == "test"

    def test_serialize_none_returns_none(self):
        assert _serialize_doc(None) is None

    def test_to_object_id_valid(self):
        valid_id = "507f1f77bcf86cd799439011"
        oid = _to_object_id(valid_id)
        assert isinstance(oid, ObjectId)

    def test_to_object_id_invalid(self):
        with pytest.raises(InvalidIdError):
            _to_object_id("not-a-valid-id")

    def test_to_object_id_empty_string(self):
        with pytest.raises(InvalidIdError):
            _to_object_id("")


class TestBaseRepositoryInit:
    """Test repository initialization."""

    def test_requires_collection_name(self, mock_db):
        class NoNameRepo(BaseRepository):
            pass
        with pytest.raises(ValueError, match="collection_name"):
            NoNameRepo(mock_db)

    def test_sets_collection(self, repo, mock_db):
        assert repo.collection is not None


@pytest.mark.asyncio
class TestInsertOne:
    """Test insert_one method."""

    async def test_returns_inserted_id(self, repo):
        oid = ObjectId()
        repo._collection.insert_one = AsyncMock(
            return_value=MagicMock(inserted_id=oid)
        )
        result = await repo.insert_one({"name": "test"})
        assert result == str(oid)

    async def test_duplicate_raises_duplicate_error(self, repo):
        from pymongo.errors import DuplicateKeyError
        repo._collection.insert_one = AsyncMock(
            side_effect=DuplicateKeyError("duplicate", details={"keyPattern": {"email": 1}})
        )
        with pytest.raises(DuplicateDocumentError) as exc_info:
            await repo.insert_one({"email": "dup@test.com"})
        assert exc_info.value.field == "email"

    async def test_pymongo_error_raises_repo_error(self, repo):
        from pymongo.errors import PyMongoError
        repo._collection.insert_one = AsyncMock(
            side_effect=PyMongoError("connection lost")
        )
        with pytest.raises(RepositoryError):
            await repo.insert_one({"name": "test"})


@pytest.mark.asyncio
class TestFindById:
    """Test find_by_id method."""

    async def test_returns_serialized_doc(self, repo):
        oid = ObjectId()
        repo._collection.find_one = AsyncMock(
            return_value={"_id": oid, "name": "test"}
        )
        result = await repo.find_by_id(str(oid))
        assert result["id"] == str(oid)
        assert result["name"] == "test"
        assert "_id" not in result

    async def test_returns_none_when_not_found(self, repo):
        repo._collection.find_one = AsyncMock(return_value=None)
        result = await repo.find_by_id("507f1f77bcf86cd799439011")
        assert result is None

    async def test_invalid_id_raises(self, repo):
        with pytest.raises(InvalidIdError):
            await repo.find_by_id("bad-id")


@pytest.mark.asyncio
class TestFindMany:
    """Test find_many method with pagination."""

    async def test_returns_list_of_serialized_docs(self, repo):
        oid1 = ObjectId()
        oid2 = ObjectId()
        cursor_mock = AsyncMock()
        cursor_mock.sort = MagicMock(return_value=cursor_mock)
        cursor_mock.skip = MagicMock(return_value=cursor_mock)
        cursor_mock.limit = MagicMock(return_value=cursor_mock)
        cursor_mock.to_list = AsyncMock(return_value=[
            {"_id": oid1, "n": 1},
            {"_id": oid2, "n": 2},
        ])
        repo._collection.find = MagicMock(return_value=cursor_mock)

        results = await repo.find_many({}, limit=10)
        assert len(results) == 2
        assert results[0]["id"] == str(oid1)

    async def test_limit_capped_at_200(self, repo):
        cursor_mock = AsyncMock()
        cursor_mock.sort = MagicMock(return_value=cursor_mock)
        cursor_mock.skip = MagicMock(return_value=cursor_mock)
        cursor_mock.limit = MagicMock(return_value=cursor_mock)
        cursor_mock.to_list = AsyncMock(return_value=[])
        repo._collection.find = MagicMock(return_value=cursor_mock)

        await repo.find_many({}, limit=999)
        cursor_mock.limit.assert_called_with(200)

    async def test_limit_minimum_is_1(self, repo):
        cursor_mock = AsyncMock()
        cursor_mock.sort = MagicMock(return_value=cursor_mock)
        cursor_mock.skip = MagicMock(return_value=cursor_mock)
        cursor_mock.limit = MagicMock(return_value=cursor_mock)
        cursor_mock.to_list = AsyncMock(return_value=[])
        repo._collection.find = MagicMock(return_value=cursor_mock)

        await repo.find_many({}, limit=0)
        cursor_mock.limit.assert_called_with(1)


@pytest.mark.asyncio
class TestUpdateOne:
    """Test update_one method."""

    async def test_returns_true_when_modified(self, repo):
        repo._collection.update_one = AsyncMock(
            return_value=MagicMock(modified_count=1)
        )
        result = await repo.update_one(
            "507f1f77bcf86cd799439011",
            {"$set": {"name": "updated"}},
        )
        assert result is True

    async def test_returns_false_when_not_found(self, repo):
        repo._collection.update_one = AsyncMock(
            return_value=MagicMock(modified_count=0)
        )
        result = await repo.update_one(
            "507f1f77bcf86cd799439011",
            {"$set": {"name": "updated"}},
        )
        assert result is False


@pytest.mark.asyncio
class TestDeleteOne:
    """Test delete_one method."""

    async def test_returns_true_when_deleted(self, repo):
        repo._collection.delete_one = AsyncMock(
            return_value=MagicMock(deleted_count=1)
        )
        result = await repo.delete_one("507f1f77bcf86cd799439011")
        assert result is True

    async def test_returns_false_when_not_found(self, repo):
        repo._collection.delete_one = AsyncMock(
            return_value=MagicMock(deleted_count=0)
        )
        result = await repo.delete_one("507f1f77bcf86cd799439011")
        assert result is False
