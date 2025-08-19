from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid

from pydantic import ConfigDict

class Tenant(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str
    domain: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(from_attributes=True)

class User(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    tenant_id: uuid.UUID
    username: str
    email: str
    hashed_password: str
    role: str  # e.g., 'admin', 'user'
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(from_attributes=True)


class UserDTO(BaseModel):
    id: uuid.UUID
    username: str
    email: str
    role: str
    tenant_id: uuid.UUID
    
    model_config = ConfigDict(from_attributes=True)


class Project(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    tenant_id: uuid.UUID
    name: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(from_attributes=True)


class ProjectUser(BaseModel):
    project_id: uuid.UUID
    user_id: uuid.UUID
    role: str = "member"
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(from_attributes=True)


class Assignee(BaseModel):
    id: uuid.UUID
    username: str
    email: str
    
    model_config = ConfigDict(from_attributes=True)

class Task(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    project_id: uuid.UUID
    title: str
    description: Optional[str] = None
    status: str  # e.g., 'todo', 'in_progress', 'in_review', 'done'
    assignee_id: Optional[uuid.UUID] = None
    assignee: Optional[Assignee] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    due_date: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
    
    def assign_to(self, user: 'User') -> None:
        """Assign this task to a user."""
        self.assignee_id = user.id
        self.assignee = Assignee(
            id=user.id,
            username=user.username,
            email=user.email
        )
    
    def unassign(self) -> None:
        """Remove assignment from this task."""
        self.assignee_id = None
        self.assignee = None
