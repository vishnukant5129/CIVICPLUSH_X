from typing import List, Optional

from pydantic import BaseModel, Field

from app.domain.enums import UserRole, UserStatus, DepartmentStatus


class CreateDepartmentRequest(BaseModel):
    name: str
    code: str
    description: Optional[str] = None


class CreateWardRequest(BaseModel):
    name: str
    code: str
    description: Optional[str] = None


class CreateAuthorityRequest(BaseModel):
    email: str
    display_name: str
    role: UserRole
    department_id: Optional[str] = None
    ward_ids: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)


class AuthorityUpdateScopeRequest(BaseModel):
    role: Optional[UserRole] = None
    department_id: Optional[str] = None
    ward_ids: Optional[List[str]] = None
    permissions: Optional[List[str]] = None
    status: Optional[UserStatus] = None

class UpdateDepartmentRequest(BaseModel):
    name: Optional[str] = None
    status: Optional[DepartmentStatus] = None

class UpdateWardRequest(BaseModel):
    name: Optional[str] = None
    status: Optional[DepartmentStatus] = None

class CreateRoutingRuleRequest(BaseModel):
    category: str
    department_id: str
    jurisdiction: Optional[str] = None
    priority: int
    active: bool = True

class UpdateRoutingRuleRequest(BaseModel):
    priority: Optional[int] = None
    active: Optional[bool] = None
