from datetime import datetime as Datetime
from pydantic import BaseModel, EmailStr, ConfigDict, field_serializer
import uuid

# User DTOs
class UserCreateDTO(BaseModel):
    username: str
    email: EmailStr
    password: str
    tenant_name: str
    tenant_domain: str

class UserDTO(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr
    role: str
    tenant_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)

class UserLoginDTO(BaseModel):
    email: EmailStr
    password: str

class TokenDTO(BaseModel):
    access_token: str
    token_type: str

# Project DTOs
class ProjectCreateDTO(BaseModel):
    name: str
    description: str | None = None

class ProjectDTO(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None = None
    tenant_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)

# Task DTOs
class TaskCreateDTO(BaseModel):
    title: str
    description: str | None = None
    status: str
    assignee_id: uuid.UUID | None = None

class AssigneeDTO(BaseModel):
    id: uuid.UUID
    username: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class TaskDTO(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None = None
    status: str
    project_id: uuid.UUID
    assignee_id: uuid.UUID | None = None
    assignee: AssigneeDTO | None = None
    created_at: Datetime
    due_date: Datetime | None = None

    model_config = ConfigDict(from_attributes=True)
    
    @field_serializer('created_at', 'due_date')
    def serialize_dt(self, dt: Datetime | None) -> str | None:
        if dt is None:
            return None
        return dt.isoformat()

class TaskUpdateDTO(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    assignee_id: uuid.UUID | None = None
