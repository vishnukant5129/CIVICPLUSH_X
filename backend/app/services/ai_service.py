"""
CivicPulse AI — AI Service.

Handles calling the LLM provider, parsing structured output,
and persisting the analysis results securely.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import google.generativeai as genai
from pymongo.asynchronous.database import AsyncDatabase

from app.config import get_settings
from app.domain.enums import AIAnalysisStatus, CivicCategory
from app.domain.notification_schemas import EventType
from app.repositories.collections import AIAnalysisRepository, ComplaintRepository
from app.services.event_service import EventService
from app.services.notification_service import NotificationService

logger = logging.getLogger("civicpulse.ai")

SYSTEM_PROMPT = """You are CivicPulse AI, a civic intelligence classifier.
Your job is to analyze a civic complaint and extract structured metadata.

Read the user complaint.
Respond ONLY with a valid JSON object matching the exact schema provided.
Do not output Markdown formatting (like ```json), just the raw JSON object.

Schema:
{
  "category": "One of: pothole_road_damage, streetlight_electricity, water_leakage, sewage_drainage, garbage_waste, public_infrastructure, traffic_signage, other",
  "summary": "A clear, concise 1-sentence summary of the issue.",
  "severity_indicators": ["list of strings", "e.g., severe flooding, risk of injury"],
  "model_confidence": 0.95 (float between 0 and 1 representing your confidence in the category)
}
"""

class AIService:
    """Service to process complaints with AI."""

    def __init__(self, db: AsyncDatabase):
        self.db = db
        self.ai_repo = AIAnalysisRepository(db)
        self.complaint_repo = ComplaintRepository(db)
        self.settings = get_settings()

    async def analyze_complaint(self, complaint_id: str) -> Optional[Dict[str, Any]]:
        """
        Run AI analysis on a complaint. 
        In Phase 5 MVP, we pass the text of the complaint.
        """
        # Retrieve complaint
        complaint = await self.complaint_repo.find_by_id(complaint_id)
        if not complaint:
            logger.error(f"Complaint {complaint_id} not found for AI analysis.")
            return None

        # Create PENDING analysis record
        analysis_doc = {
            "complaint_id": complaint_id,
            "pipeline_version": "v1.0",
            "provider": self.settings.ai_provider,
            "model": self.settings.gemini_model,
            "status": AIAnalysisStatus.PROCESSING.value,
        }
        analysis_id = await self.ai_repo.insert_one(analysis_doc)

        # If Gemini is the provider, execute call
        if self.settings.ai_provider == "gemini":
            try:
                result_data = await self._call_gemini(complaint)
                await self._mark_completed(analysis_id, result_data)
                return await self.ai_repo.find_by_id(analysis_id)
            except Exception as e:
                logger.error(f"AI Provider failed: {e}")
                await self._mark_failed(analysis_id, str(e))
                return await self.ai_repo.find_by_id(analysis_id)
        else:
            # Unsupported provider
            error_msg = f"Unsupported AI Provider: {self.settings.ai_provider}"
            logger.error(error_msg)
            await self._mark_failed(analysis_id, error_msg)
            return await self.ai_repo.find_by_id(analysis_id)

    async def _call_gemini(self, complaint: Dict[str, Any]) -> Dict[str, Any]:
        """Call Gemini API to analyze the complaint."""
        if not self.settings.gemini_api_key:
            raise ValueError("Gemini API Key is not configured.")

        genai.configure(api_key=self.settings.gemini_api_key)
        
        user_prompt = f"Title: {complaint.get('title')}\nDescription: {complaint.get('description')}"
        
        model = genai.GenerativeModel(
            model_name=self.settings.gemini_model,
            system_instruction=SYSTEM_PROMPT,
        )

        response = await model.generate_content_async(
            user_prompt,
            generation_config={"temperature": 0.0, "response_mime_type": "application/json"}
        )

        response_content = response.text
        if not response_content:
            raise ValueError("Empty response from AI.")

        try:
            # Attempt to parse structured output
            data = json.loads(response_content.strip())
        except json.JSONDecodeError:
            raise ValueError("AI did not return valid JSON.")

        # Domain Validation
        category = data.get("category")
        try:
            valid_category = CivicCategory(category)
        except ValueError:
            # Fallback if AI hallucinates category
            data["category"] = CivicCategory.OTHER.value
            
        confidence = data.get("model_confidence")
        if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
            data["model_confidence"] = 0.5

        return data

    async def _mark_completed(self, analysis_id: str, result: Dict[str, Any]) -> None:
        """Mark analysis as successfully completed."""
        await self.ai_repo.update_one(
            {"_id": self.ai_repo._get_object_id(analysis_id)},
            {
                "$set": {
                    "status": AIAnalysisStatus.COMPLETED.value,
                    "result": result,
                    "confidence": result.get("model_confidence"),
                    "completed_at": datetime.now(timezone.utc)
                }
            }
        )
        try:
            doc = await self.ai_repo.find_by_id(analysis_id)
            if doc:
                complaint_id = doc.get("complaint_id")
                event_service = EventService(self.db)
                notification_service = NotificationService(self.db)
                event = await event_service.record_event(
                    event_type=EventType.AI_ANALYSIS_COMPLETED,
                    complaint_id=complaint_id,
                    metadata={"category": result.get("category")},
                )
                if event:
                    await notification_service.handle_domain_event(event)
        except Exception as e:
            logger.error(f"Error firing event/notification for AI analysis {analysis_id}: {e}")

    async def _mark_failed(self, analysis_id: str, error_message: str) -> None:
        """Mark analysis as failed."""
        # Sanitize error message to prevent leaking keys
        safe_error = error_message
        if self.settings.gemini_api_key and self.settings.gemini_api_key in safe_error:
            safe_error = safe_error.replace(self.settings.gemini_api_key, "[REDACTED]")

        await self.ai_repo.update_one(
            {"_id": self.ai_repo._get_object_id(analysis_id)},
            {
                "$set": {
                    "status": AIAnalysisStatus.FAILED.value,
                    "error_message": safe_error[:1000],
                    "completed_at": datetime.now(timezone.utc)
                }
            }
        )
