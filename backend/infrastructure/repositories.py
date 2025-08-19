import logging
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_
from sqlalchemy.orm import selectinload, joinedload

from domain.entities import User, Tenant, Project, Task
from domain.repositories import UserRepository, TenantRepository, ProjectRepository, TaskRepository
from infrastructure.models import UserModel, TenantModel, ProjectModel, TaskModel, ProjectUserModel

class TenantRepositoryImpl(TenantRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, tenant: Tenant) -> None:
        tenant_dict = tenant.model_dump()
        tenant_model = TenantModel(**tenant_dict)
        self.session.add(tenant_model)
        await self.session.commit()
        # Refresh the model to get the generated ID
        await self.session.refresh(tenant_model)
        # Update the original tenant with the database-generated values
        tenant.id = tenant_model.id
        tenant.created_at = tenant_model.created_at

    async def get_by_id(self, tenant_id: uuid.UUID) -> Optional[Tenant]:
        result = await self.session.get(TenantModel, tenant_id)
        if not result:
            return None
        return Tenant.model_validate(result.__dict__)
        
    async def get_by_domain(self, domain: str) -> Optional[Tenant]:
        stmt = select(TenantModel).where(TenantModel.domain == domain)
        result = await self.session.execute(stmt)
        tenant = result.scalar_one_or_none()
        if not tenant:
            return None
        return Tenant.model_validate(tenant.__dict__)

class UserRepositoryImpl(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, user: User) -> None:
        user_dict = user.model_dump()
        user_model = UserModel(**user_dict)
        self.session.add(user_model)
        await self.session.commit()
        # Refresh the model to get the generated ID
        await self.session.refresh(user_model)
        # Update the original user with the database-generated values
        user.id = user_model.id
        user.created_at = user_model.created_at

    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        result = await self.session.get(UserModel, user_id)
        if not result:
            return None
        return User.model_validate(result.__dict__)

    async def get_by_username(self, username: str) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.username == username)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            return None
        return User.model_validate(user.__dict__)

    async def get_by_email(self, email: str) -> Optional[User]:
        logger = logging.getLogger(__name__)
        logger.info(f"[UserRepository] Looking up user with email: {email}")
        try:
            stmt = select(UserModel).where(UserModel.email == email)
            logger.debug(f"[UserRepository] Executing query: {stmt}")
            
            result = await self.session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                logger.warning(f"[UserRepository] No user found with email: {email}")
                return None
                
            logger.info(f"[UserRepository] Found user: {user.email}, ID: {user.id}")
            logger.debug(f"[UserRepository] User data: {user.__dict__}")
            
            user_dict = user.__dict__.copy()
            # Remove SQLAlchemy instance state before validation
            user_dict.pop('_sa_instance_state', None)
            
            try:
                validated_user = User.model_validate(user_dict)
                logger.debug(f"[UserRepository] Successfully validated user: {validated_user}")
                return validated_user
            except Exception as validation_error:
                logger.error(f"[UserRepository] Validation error for user {email}: {str(validation_error)}")
                logger.debug(f"[UserRepository] User dict that failed validation: {user_dict}")
                raise
                
        except Exception as e:
            logger.error(f"[UserRepository] Error looking up user with email {email}: {str(e)}", exc_info=True)
            raise

class ProjectRepositoryImpl(ProjectRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, project: Project) -> None:
        # Exclude updated_at as it's managed by SQLAlchemy's onupdate
        project_dict = project.model_dump(exclude={'updated_at'})
        project_model = ProjectModel(**project_dict)
        self.session.add(project_model)
        await self.session.commit()
        await self.session.refresh(project_model)
        project.id = project_model.id
        project.created_at = project_model.created_at
        project.updated_at = project_model.updated_at

    async def get_by_id(self, project_id: uuid.UUID, tenant_id: uuid.UUID) -> Optional[Project]:
        stmt = select(ProjectModel).where(
            ProjectModel.id == project_id,
            ProjectModel.tenant_id == tenant_id
        )
        result = await self.session.execute(stmt)
        project = result.scalar_one_or_none()
        if not project:
            return None
        # Convert SQLAlchemy model to dict and ensure all fields are included
        project_dict = {c.name: getattr(project, c.name) for c in project.__table__.columns}
        return Project.model_validate(project_dict)

    async def get_by_tenant_id(self, tenant_id: uuid.UUID) -> List[Project]:
        stmt = select(ProjectModel).where(ProjectModel.tenant_id == tenant_id)
        result = await self.session.execute(stmt)
        projects = result.scalars().all()
        # Convert SQLAlchemy models to dicts and ensure all fields are included
        return [Project.model_validate({c.name: getattr(p, c.name) for c in p.__table__.columns}) for p in projects]

    async def update(self, project: Project) -> Project:
        # First get the existing project to ensure it exists and get the current values
        stmt = select(ProjectModel).where(
            ProjectModel.id == project.id,
            ProjectModel.tenant_id == project.tenant_id
        )
        result = await self.session.execute(stmt)
        project_model = result.scalar_one_or_none()
        
        if not project_model:
            raise ValueError(f"Project with ID {project.id} not found or access denied")
        
        # Update the project model with the new values
        project_dict = project.model_dump(exclude_unset=True, exclude={'updated_at'})
        for key, value in project_dict.items():
            if key != 'id' and key != 'tenant_id' and key != 'created_at':
                setattr(project_model, key, value)
        
        # The updated_at field is automatically updated by SQLAlchemy's onupdate
        
        await self.session.commit()
        await self.session.refresh(project_model)
        
        # Update the original project with any database-generated values
        project.updated_at = project_model.updated_at
        project.created_at = project_model.created_at
        
        return project

    async def delete(self, project_id: uuid.UUID, tenant_id: uuid.UUID) -> bool:
        logger = logging.getLogger(__name__)
        logger.info(f"Attempting to delete project {project_id} for tenant {tenant_id}")
        
        try:
            # First, verify the project exists and belongs to the tenant
            stmt = select(ProjectModel).where(
                ProjectModel.id == project_id,
                ProjectModel.tenant_id == tenant_id
            )
            
            logger.debug(f"Executing query: {stmt}")
            result = await self.session.execute(stmt)
            project = result.scalar_one_or_none()
            
            if not project:
                logger.warning(f"Project {project_id} not found or not accessible by tenant {tenant_id}")
                return False
                
            logger.info(f"Found project {project_id}, proceeding with deletion")
            
            # Delete related tasks
            delete_tasks = delete(TaskModel).where(TaskModel.project_id == project_id)
            await self.session.execute(delete_tasks)
            logger.info(f"Deleted tasks for project {project_id}")
            
            # Delete project-user associations
            delete_project_users = delete(ProjectUserModel).where(
                ProjectUserModel.project_id == project_id
            )
            await self.session.execute(delete_project_users)
            logger.info(f"Deleted project-user associations for project {project_id}")
            
            # Finally, delete the project itself
            await self.session.delete(project)
            await self.session.commit()
            
            logger.info(f"Successfully deleted project {project_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting project {project_id}: {str(e)}", exc_info=True)
            await self.session.rollback()
            raise

class TaskRepositoryImpl(TaskRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, task: Task) -> None:
        task_dict = task.model_dump()
        task_model = TaskModel(**task_dict)
        self.session.add(task_model)
        await self.session.commit()
        await self.session.refresh(task_model)
        task.id = task_model.id
        task.created_at = task_model.created_at

    async def get_by_id(self, task_id: uuid.UUID) -> Optional[Task]:
        stmt = (
            select(TaskModel)
            .options(selectinload(TaskModel.assignee))
            .where(TaskModel.id == task_id)
        )
        result = await self.session.execute(stmt)
        task = result.scalar_one_or_none()
        if not task:
            return None
        
        task_dict = task.__dict__.copy()
        if task.assignee:
            task_dict['assignee'] = task.assignee.__dict__
        return Task.model_validate(task_dict)

    async def get_by_project_id(self, project_id: uuid.UUID) -> List[Task]:
        stmt = (
            select(TaskModel)
            .options(selectinload(TaskModel.assignee))
            .where(TaskModel.project_id == project_id)
        )
        result = await self.session.execute(stmt)
        tasks = result.scalars().all()
        
        task_list = []
        for task in tasks:
            task_dict = task.__dict__.copy()
            if task.assignee:
                task_dict['assignee'] = task.assignee.__dict__
            task_list.append(Task.model_validate(task_dict))
            
        return task_list

    async def update(self, task: Task) -> None:
        # Get the task model from the database
        task_model = await self.session.get(TaskModel, task.id)
        if not task_model:
            raise ValueError(f"Task with ID {task.id} not found")
            
        # Convert task to dict and update the model
        task_dict = task.model_dump(exclude_unset=True)
        for key, value in task_dict.items():
            # Skip internal attributes
            if not key.startswith('_'):
                setattr(task_model, key, value)
                
        # Handle assignee separately if present
        if hasattr(task, 'assignee') and task.assignee is not None:
            if not hasattr(task, 'assignee_id') or task.assignee_id is None:
                task_model.assignee_id = task.assignee.id
        
        # Commit the changes
        self.session.add(task_model)
        await self.session.commit()
        await self.session.refresh(task_model)

    async def delete(self, task_id: uuid.UUID) -> bool:
        task = await self.session.get(TaskModel, task_id)
        if task:
            await self.session.delete(task)
            await self.session.commit()
            return True
        return False
