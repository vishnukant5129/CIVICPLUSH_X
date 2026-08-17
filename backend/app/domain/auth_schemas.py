"""
CivicPulse AI — API Schemas for Authentication.

These are the public API request/response schemas, distinct from the
internal database domain schemas (app/domain/schemas.py).
"""

from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.domain.enums import UserRole


class RegisterRequest(BaseModel):
    """Payload for citizen registration."""
    email: str = Field(..., max_length=254)
    display_name: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        """Basic email format check."""
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email format.")
        return v.strip()


class LoginRequest(BaseModel):
    """Payload for user login."""
    email: str = Field(..., max_length=254)
    password: str = Field(..., min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def trim_email(cls, v: str) -> str:
        return v.strip()


class UserResponse(BaseModel):
    """Safe public representation of a user (excludes password hashes)."""
    id: str
    email: str
    display_name: str
    role: UserRole
    department_id: Optional[str] = None
    ward_ids: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)

