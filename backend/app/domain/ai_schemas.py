"""
CivicPulse AI — API Schemas for AI Analysis.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from app.domain.enums import AIAnalysisStatus


class AIAnalysisResponse(BaseModel):
    """Safe public representation of AI Analysis."""
    id: str
    complaint_id: str
    provider: str
    status: AIAnalysisStatus
    result: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    # We do NOT expose error_message or model versions to the end user
    # to avoid leaking internals or raw provider errors.
