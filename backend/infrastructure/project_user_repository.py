from typing import List, Optional
import uuid
from sqlalchemy import select, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities import User, ProjectUser, Project
from domain.repositories import ProjectUserRepository
from infrastructure.models import UserModel, ProjectUserModel

class ProjectUserRepositoryImpl(ProjectUserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_user_to_project(self, project_id: uuid.UUID, user_id: uuid.UUID, role: str = 'member') -> None:
        project_user = ProjectUserModel(
            project_id=project_id,
            user_id=user_id,
            role=role
        )
        self.session.add(project_user)
        await self.session.commit()

    async def remove_user_from_project(self, project_id: uuid.UUID, user_id: uuid.UUID) -> None:
        stmt = delete(ProjectUserModel).where(
            and_(
                ProjectUserModel.project_id == project_id,
                ProjectUserModel.user_id == user_id
            )
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def get_users_by_project(self, project_id: uuid.UUID, tenant_id: uuid.UUID) -> List[User]:
        stmt = (
            select(UserModel)
            .join(ProjectUserModel, UserModel.id == ProjectUserModel.user_id)
            .where(
                and_(
                    ProjectUserModel.project_id == project_id,
                    UserModel.tenant_id == tenant_id
                )
            )
        )
        result = await self.session.execute(stmt)
        users = result.scalars().all()
        return [User.model_validate(user.__dict__) for user in users]

    async def get_projects_by_user(self, user_id: uuid.UUID) -> List[Project]:
        from infrastructure.models import ProjectModel  # Import here to avoid circular imports
        
        stmt = (
            select(ProjectModel)
            .join(ProjectUserModel, ProjectModel.id == ProjectUserModel.project_id)
            .where(ProjectUserModel.user_id == user_id)
        )
        
        result = await self.session.execute(stmt)
        projects = result.scalars().all()
        return [Project.model_validate(project.__dict__) for project in projects] if projects else []

    async def get_project_user_role(self, project_id: uuid.UUID, user_id: uuid.UUID) -> Optional[str]:
        stmt = select(ProjectUserModel.role).where(
            and_(
                ProjectUserModel.project_id == project_id,
                ProjectUserModel.user_id == user_id
            )
        )
        result = await self.session.execute(stmt)
        role = result.scalar_one_or_none()
        return role if role else None
