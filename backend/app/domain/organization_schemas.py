from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from app.domain.enums import OrganizationType, OrganizationVerificationStatus

class OrganizationCreateRequest(BaseModel):
    name: str = Field(..., max_length=200)
    org_type: OrganizationType
    description: Optional[str] = Field(default=None, max_length=2000)
    website: Optional[str] = Field(default=None, max_length=500)
    contact_email: Optional[str] = Field(default=None, max_length=254)
    contact_phone: Optional[str] = Field(default=None, max_length=50)
    service_regions: List[str] = Field(default_factory=list)
    focus_areas: List[str] = Field(default_factory=list)
    capabilities: List[str] = Field(default_factory=list)

class OrganizationResponse(BaseModel):
    id: str
    name: str
    org_type: OrganizationType
    description: Optional[str] = None
    website: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    service_regions: List[str] = Field(default_factory=list)
    focus_areas: List[str] = Field(default_factory=list)
    capabilities: List[str] = Field(default_factory=list)
    verification_status: OrganizationVerificationStatus
    created_at: datetime
    updated_at: datetime
