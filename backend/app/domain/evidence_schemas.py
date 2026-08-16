"""
CivicPulse AI — API Schemas for Evidence.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.domain.enums import EvidenceProcessingStatus


class EvidenceResponse(BaseModel):
    """Safe public representation of evidence."""
    id: str
    complaint_id: str
    user_id: str
    original_filename: str
    mime_type: str
    size_bytes: int
    processing_status: EvidenceProcessingStatus
    created_at: datetime
    
    # We intentionally do not expose the absolute storage key/path.
    # In a full phase we might provide an authorized presigned URL here.
