from abc import ABC, abstractmethod
from typing import List, Optional
import uuid

from .entities import User, Tenant, Project, Task, ProjectUser

class TenantRepository(ABC):
    @abstractmethod
    async def add(self, tenant: Tenant) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, tenant_id: uuid.UUID) -> Optional[Tenant]:
        pass
        
    @abstractmethod
    async def get_by_domain(self, domain: str) -> Optional[Tenant]:
        pass

class UserRepository(ABC):
    @abstractmethod
    async def add(self, user: User) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        pass

class ProjectRepository(ABC):
    @abstractmethod
    async def add(self, project: Project) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, project_id: uuid.UUID, tenant_id: uuid.UUID) -> Optional[Project]:
        pass

    @abstractmethod
    async def get_by_tenant_id(self, tenant_id: uuid.UUID) -> List[Project]:
        pass

    @abstractmethod
    async def update(self, project: Project) -> None:
        pass
        
    @abstractmethod
    async def delete(self, project_id: uuid.UUID, tenant_id: uuid.UUID) -> None:
        pass

class TaskRepository(ABC):
    @abstractmethod
    async def add(self, task: Task) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, task_id: uuid.UUID) -> Optional[Task]:
        pass

    @abstractmethod
    async def get_by_project_id(self, project_id: uuid.UUID) -> List[Task]:
        pass

    @abstractmethod
    async def update(self, task: Task) -> None:
        pass

    @abstractmethod
    async def delete(self, task_id: uuid.UUID) -> None:
        pass


class ProjectUserRepository(ABC):
    @abstractmethod
    async def add_user_to_project(self, project_id: uuid.UUID, user_id: uuid.UUID, role: str = 'member') -> None:
        pass
        
    @abstractmethod
    async def remove_user_from_project(self, project_id: uuid.UUID, user_id: uuid.UUID) -> None:
        pass
        
    @abstractmethod
    async def get_users_by_project(self, project_id: uuid.UUID, tenant_id: uuid.UUID) -> List[User]:
        pass
        
    @abstractmethod
    async def get_projects_by_user(self, user_id: uuid.UUID) -> List[Project]:
        pass
        
    @abstractmethod
    async def get_project_user_role(self, project_id: uuid.UUID, user_id: uuid.UUID) -> Optional[str]:
        pass
