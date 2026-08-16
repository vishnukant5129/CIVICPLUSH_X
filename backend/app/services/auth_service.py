"""
CivicPulse AI — Authentication Service.

Handles password hashing, session management via Redis,
and identity validation.

Security:
- Passwords hashed with passlib (bcrypt).
- Sessions backed by Redis, tokens are 32-byte secure random strings.
- Immediate revocation on logout.
"""

from __future__ import annotations

import json
import logging
import secrets
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from passlib.context import CryptContext
from pydantic import ValidationError

from app.config import get_settings
from app.database import redis
from app.domain.enums import UserRole

logger = logging.getLogger("civicpulse.auth")

# Modern bcrypt config
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Authentication and session management."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password securely."""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against a hash."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    async def create_session(user_id: str, role: UserRole) -> str:
        """
        Create a secure session backed by Redis.

        Returns:
            The opaque session ID to be set in the cookie.
        """
        session_id = secrets.token_urlsafe(32)
        key = f"session:{session_id}"
        
        session_data = {
            "user_id": user_id,
            "role": role.value,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        settings = get_settings()
        client = redis.get_client()
        if client is None:
            raise RuntimeError("Redis is not available for session storage.")
            
        await client.setex(
            key,
            settings.session_max_age_seconds,
            json.dumps(session_data)
        )
        return session_id

    @staticmethod
    async def get_session(session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve session data from Redis.
        Also extends the expiration on access (rolling session).
        """
        key = f"session:{session_id}"
        client = redis.get_client()
        if client is None:
            return None
            
        data = await client.get(key)
        if not data:
            return None
            
        # Rolling session: extend TTL
        settings = get_settings()
        await client.expire(key, settings.session_max_age_seconds)
        
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            logger.error("Invalid JSON in Redis session %s", session_id)
            return None

    @staticmethod
    async def destroy_session(session_id: str) -> None:
        """
        Destroy a session, logging the user out instantly.
        """
        key = f"session:{session_id}"
        client = redis.get_client()
        if client is not None:
            await client.delete(key)
