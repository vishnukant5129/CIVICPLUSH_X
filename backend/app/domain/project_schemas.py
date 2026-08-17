from typing import List, Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field

from app.domain.enums import CivicCategory, CivicProjectStatus, MatchRequestStatus

class CivicProjectCreateRequest(BaseModel):
    title: str = Field(..., max_length=300)
    description: str = Field(..., max_length=5000)
    problem_cluster_id: Optional[str] = None
    category: CivicCategory
    subcategory: Optional[str] = None
    department_id: Optional[str] = None
    ward_id: Optional[str] = None
    severity: Optional[str] = None
    priority: Optional[str] = None
    estimated_affected_population: Optional[int] = None
    estimated_cost_min: Optional[float] = None
    estimated_cost_max: Optional[float] = None
    currency: Optional[str] = Field(default="INR")
    required_resources: List[str] = Field(default_factory=list)
    impact_summary: Optional[str] = None

class CivicProjectResponse(BaseModel):
    id: str
    project_code: str
    title: str
    description: str
    problem_cluster_id: Optional[str] = None
    category: CivicCategory
    subcategory: Optional[str] = None
    department_id: Optional[str] = None
    ward_id: Optional[str] = None
    status: CivicProjectStatus
    severity: Optional[str] = None
    priority: Optional[str] = None
    estimated_affected_population: Optional[int] = None
    estimated_cost_min: Optional[float] = None
    estimated_cost_max: Optional[float] = None
    currency: Optional[str] = None
    required_resources: List[str] = Field(default_factory=list)
    impact_summary: Optional[str] = None
    verification_status: str
    created_at: datetime
    updated_at: datetime

class ResourceMatchRequestCreate(BaseModel):
    project_id: str
    organization_id: str
    resource_type: str
    message: Optional[str] = None

class ResourceMatchRequestResponse(BaseModel):
    id: str
    project_id: str
    organization_id: str
    resource_type: str
    message: Optional[str] = None
    status: MatchRequestStatus
    created_at: datetime
    updated_at: datetime
