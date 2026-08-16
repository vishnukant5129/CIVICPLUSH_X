"""
CivicPulse AI — Evidence Service.

Handles secure file upload, validation, local storage (MVP),
and metadata creation.
"""

import asyncio
import logging
import os
import uuid
from typing import Any, Dict, List

import aiofiles
from fastapi import UploadFile
from pymongo.asynchronous.database import AsyncDatabase

from app.config import get_settings
from app.domain.enums import EvidenceProcessingStatus
from app.repositories.collections import ComplaintRepository, EvidenceRepository

logger = logging.getLogger("civicpulse.evidence")

# MVP Supported file types
SUPPORTED_MIME_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "application/pdf": ".pdf"
}

class EvidenceService:
    def __init__(self, db: AsyncDatabase):
        self.db = db
        self.evidence_repo = EvidenceRepository(db)
        self.complaint_repo = ComplaintRepository(db)
        self.settings = get_settings()

    async def upload_evidence(
        self, complaint_id: str, user_id: str, file: UploadFile
    ) -> Dict[str, Any]:
        """Validate, store, and create evidence metadata."""
        
        # 1. Verify Ownership
        complaint = await self.complaint_repo.find_by_id(complaint_id)
        if not complaint:
            raise ValueError("Complaint not found.")
        if complaint.get("user_id") != user_id:
            raise PermissionError("Unauthorized to upload evidence for this complaint.")

        # 2. Validate MIME Type
        if file.content_type not in SUPPORTED_MIME_TYPES:
            raise ValueError(f"Unsupported file type. Supported: {list(SUPPORTED_MIME_TYPES.keys())}")

        # 3. Read and Validate Size
        # We read chunk by chunk to avoid loading huge files entirely into memory
        file_bytes = await file.read()
        size_bytes = len(file_bytes)
        if size_bytes > self.settings.max_upload_size_bytes:
            raise ValueError(f"File exceeds maximum allowed size ({self.settings.max_upload_size_bytes} bytes).")

        # 4. Generate Storage Key (Prevents path traversal and filename injection)
        ext = SUPPORTED_MIME_TYPES[file.content_type]
        unique_id = str(uuid.uuid4())
        storage_key = f"{complaint_id}/{unique_id}{ext}"
        
        # Ensure directory exists
        storage_dir = os.path.join(self.settings.storage_path, complaint_id)
        os.makedirs(storage_dir, exist_ok=True)
        
        absolute_path = os.path.join(storage_dir, f"{unique_id}{ext}")

        # 5. Save to local storage
        try:
            async with aiofiles.open(absolute_path, 'wb') as out_file:
                await out_file.write(file_bytes)
        except Exception as e:
            logger.error(f"Failed to write evidence to {absolute_path}: {e}")
            raise RuntimeError("Storage failure. Evidence could not be saved.")

        # 6. Create Metadata
        evidence_doc = {
            "complaint_id": complaint_id,
            "user_id": user_id,
            "storage_key": storage_key,
            "original_filename": file.filename or "unknown",
            "mime_type": file.content_type,
            "size_bytes": size_bytes,
            "processing_status": EvidenceProcessingStatus.PENDING.value,
        }
        
        evidence_id = await self.evidence_repo.insert_one(evidence_doc)
        
        # Update complaint evidence count safely
        await self.complaint_repo.update_one(
            {"_id": self.complaint_repo._get_object_id(complaint_id)},
            {"$inc": {"evidence_count": 1}}
        )

        return await self.evidence_repo.find_by_id(evidence_id)

    async def get_evidence_for_complaint(self, complaint_id: str, user_id: str) -> List[Dict[str, Any]]:
        """Get all evidence metadata for a complaint, checking ownership."""
        complaint = await self.complaint_repo.find_by_id(complaint_id)
        if not complaint or complaint.get("user_id") != user_id:
            return []
            
        return await self.evidence_repo.find_by_complaint(complaint_id)
