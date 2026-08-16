"""
CivicPulse AI — Base Repository.

Provides reusable async MongoDB repository primitives.

All collection-specific repositories inherit from BaseRepository.

This base handles:
    - CRUD operations
    - Pagination
    - Error translation
    - Consistent _id handling

Repositories do NOT contain:
    - HTTP/API logic
    - Authorization logic
    - AI/LLM logic
    - Frontend logic
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

from bson import ObjectId
from bson.errors import InvalidId
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.errors import DuplicateKeyError, PyMongoError

logger = logging.getLogger("civicpulse.repository")


class RepositoryError(Exception):
    """Base exception for repository-level errors."""
    pass


class DocumentNotFoundError(RepositoryError):
    """Raised when a requested document does not exist."""
    pass


class DuplicateDocumentError(RepositoryError):
    """Raised when a unique constraint is violated."""

    def __init__(self, message: str = "Document already exists.", field: str | None = None):
        self.field = field
        super().__init__(message)


class InvalidIdError(RepositoryError):
    """Raised when a provided ID is not a valid ObjectId."""
    pass


def _to_object_id(id_str: str) -> ObjectId:
    """
    Convert a string ID to ObjectId.

    Raises InvalidIdError if the string is not a valid ObjectId.
    """
    try:
        return ObjectId(id_str)
    except (InvalidId, TypeError) as exc:
        raise InvalidIdError(f"Invalid ID format: '{id_str}'") from exc


def _serialize_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert MongoDB document for application use.

    Converts ObjectId _id to string 'id' field.
    """
    if doc is None:
        return doc
    result = dict(doc)
    if "_id" in result:
        result["id"] = str(result.pop("_id"))
    return result


class BaseRepository:
    """
    Async MongoDB repository with common CRUD and pagination primitives.

    Subclass for each collection, providing collection_name.
    """

    collection_name: str = ""

    def __init__(self, db: AsyncDatabase):
        if not self.collection_name:
            raise ValueError("collection_name must be set on the repository subclass.")
        self._db = db
        self._collection: AsyncCollection = db[self.collection_name]

    @property
    def collection(self) -> AsyncCollection:
        """Access the underlying MongoDB collection."""
        return self._collection

    # --- Create ---

    async def insert_one(self, document: Dict[str, Any]) -> str:
        """
        Insert a single document.

        Args:
            document: The document dict to insert.

        Returns:
            The inserted document's ID as string.

        Raises:
            DuplicateDocumentError: If a unique constraint is violated.
            RepositoryError: On other database errors.
        """
        try:
            result = await self._collection.insert_one(document)
            return str(result.inserted_id)
        except DuplicateKeyError as exc:
            # Extract the duplicate key field name if possible
            details = exc.details or {}
            key_pattern = details.get("keyPattern", {})
            field = next(iter(key_pattern), None) if key_pattern else None
            raise DuplicateDocumentError(
                f"Duplicate value in collection '{self.collection_name}'.",
                field=field,
            ) from exc
        except PyMongoError as exc:
            logger.error(
                "Insert failed in %s: %s", self.collection_name, str(exc)
            )
            raise RepositoryError(
                f"Database insert failed in '{self.collection_name}'."
            ) from exc

    # --- Read ---

    async def find_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Find a document by its _id.

        Args:
            doc_id: The document ID as string.

        Returns:
            Serialized document dict or None.

        Raises:
            InvalidIdError: If doc_id is not a valid ObjectId.
        """
        oid = _to_object_id(doc_id)
        try:
            doc = await self._collection.find_one({"_id": oid})
            return _serialize_doc(doc) if doc else None
        except PyMongoError as exc:
            logger.error(
                "Find by ID failed in %s: %s", self.collection_name, str(exc)
            )
            raise RepositoryError(
                f"Database query failed in '{self.collection_name}'."
            ) from exc

    async def find_one(self, filter: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Find a single document matching a filter.

        Args:
            filter: MongoDB query filter dict.

        Returns:
            Serialized document dict or None.
        """
        try:
            doc = await self._collection.find_one(filter)
            return _serialize_doc(doc) if doc else None
        except PyMongoError as exc:
            logger.error(
                "Find one failed in %s: %s", self.collection_name, str(exc)
            )
            raise RepositoryError(
                f"Database query failed in '{self.collection_name}'."
            ) from exc

    async def find_many(
        self,
        filter: Dict[str, Any],
        *,
        sort: Optional[List[Tuple[str, int]]] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Find multiple documents with pagination.

        Args:
            filter: MongoDB query filter dict.
            sort: List of (field, direction) tuples.
            skip: Number of documents to skip (pagination offset).
            limit: Maximum documents to return. Capped at 200.

        Returns:
            List of serialized document dicts.
        """
        # Cap limit to prevent unbounded queries
        safe_limit = min(max(limit, 1), 200)

        try:
            cursor = self._collection.find(filter)
            if sort:
                cursor = cursor.sort(sort)
            cursor = cursor.skip(skip).limit(safe_limit)
            docs = await cursor.to_list(length=safe_limit)
            return [_serialize_doc(d) for d in docs]
        except PyMongoError as exc:
            logger.error(
                "Find many failed in %s: %s", self.collection_name, str(exc)
            )
            raise RepositoryError(
                f"Database query failed in '{self.collection_name}'."
            ) from exc

    async def count(self, filter: Dict[str, Any]) -> int:
        """
        Count documents matching a filter.

        Args:
            filter: MongoDB query filter dict.

        Returns:
            Document count.
        """
        try:
            return await self._collection.count_documents(filter)
        except PyMongoError as exc:
            logger.error(
                "Count failed in %s: %s", self.collection_name, str(exc)
            )
            raise RepositoryError(
                f"Database count failed in '{self.collection_name}'."
            ) from exc

    # --- Update ---

    async def update_one(
        self,
        doc_id: str,
        update: Dict[str, Any],
    ) -> bool:
        """
        Update a single document by ID.

        Args:
            doc_id: Document ID as string.
            update: MongoDB update operations (e.g. {"$set": {...}}).

        Returns:
            True if a document was modified, False if not found.

        Raises:
            InvalidIdError: If doc_id is not valid.
            DuplicateDocumentError: If update violates a unique constraint.
        """
        oid = _to_object_id(doc_id)
        try:
            result = await self._collection.update_one({"_id": oid}, update)
            return result.modified_count > 0
        except DuplicateKeyError as exc:
            details = exc.details or {}
            key_pattern = details.get("keyPattern", {})
            field = next(iter(key_pattern), None) if key_pattern else None
            raise DuplicateDocumentError(
                f"Duplicate value in collection '{self.collection_name}'.",
                field=field,
            ) from exc
        except PyMongoError as exc:
            logger.error(
                "Update failed in %s: %s", self.collection_name, str(exc)
            )
            raise RepositoryError(
                f"Database update failed in '{self.collection_name}'."
            ) from exc

    async def update_many(
        self,
        filter: Dict[str, Any],
        update: Dict[str, Any],
    ) -> int:
        """
        Update multiple documents matching a filter.

        Args:
            filter: MongoDB query filter dict.
            update: MongoDB update operations.

        Returns:
            Number of modified documents.
        """
        try:
            result = await self._collection.update_many(filter, update)
            return result.modified_count
        except PyMongoError as exc:
            logger.error(
                "Update many failed in %s: %s", self.collection_name, str(exc)
            )
            raise RepositoryError(
                f"Database update failed in '{self.collection_name}'."
            ) from exc

    # --- Delete ---

    async def delete_one(self, doc_id: str) -> bool:
        """
        Delete a single document by ID.

        Returns:
            True if a document was deleted, False if not found.
        """
        oid = _to_object_id(doc_id)
        try:
            result = await self._collection.delete_one({"_id": oid})
            return result.deleted_count > 0
        except PyMongoError as exc:
            logger.error(
                "Delete failed in %s: %s", self.collection_name, str(exc)
            )
            raise RepositoryError(
                f"Database delete failed in '{self.collection_name}'."
            ) from exc

    # --- Geospatial ---

    async def find_near(
        self,
        field: str,
        longitude: float,
        latitude: float,
        max_distance_meters: float,
        *,
        filter: Optional[Dict[str, Any]] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Find documents near a geographic point.

        Uses MongoDB $near with 2dsphere index.

        Args:
            field: The GeoJSON field path (e.g. "location.geo").
            longitude: Query point longitude.
            latitude: Query point latitude.
            max_distance_meters: Maximum distance in meters.
            filter: Additional filter criteria.
            limit: Maximum results.

        Returns:
            List of serialized documents sorted by distance.
        """
        safe_limit = min(max(limit, 1), 200)

        query: Dict[str, Any] = {
            field: {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [longitude, latitude],
                    },
                    "$maxDistance": max_distance_meters,
                }
            }
        }
        if filter:
            query.update(filter)

        try:
            cursor = self._collection.find(query).limit(safe_limit)
            docs = await cursor.to_list(length=safe_limit)
            return [_serialize_doc(d) for d in docs]
        except PyMongoError as exc:
            logger.error(
                "Geospatial query failed in %s: %s", self.collection_name, str(exc)
            )
            raise RepositoryError(
                f"Geospatial query failed in '{self.collection_name}'."
            ) from exc
