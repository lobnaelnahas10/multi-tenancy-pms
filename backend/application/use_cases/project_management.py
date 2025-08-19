import uuid
from typing import List
from datetime import datetime

from domain.entities import Project, Task
from domain.repositories import ProjectRepository, TaskRepository
from application.dtos import ProjectCreateDTO, ProjectDTO, TaskCreateDTO, TaskDTO, TaskUpdateDTO

class CreateProjectUseCase:
    def __init__(self, project_repository: ProjectRepository, project_user_repository):
        self.project_repository = project_repository
        self.project_user_repository = project_user_repository

    async def execute(self, project_data: ProjectCreateDTO, tenant_id: uuid.UUID, user_id: uuid.UUID) -> Project:
        # Create the project
        project = Project(
            name=project_data.name,
            description=project_data.description,
            tenant_id=tenant_id
        )
        await self.project_repository.add(project)
        
        # Add the creating user as an owner of the project
        await self.project_user_repository.add_user_to_project(
            project_id=project.id,
            user_id=user_id,
            role='owner'
        )
        
        return project

class GetProjectsByTenantUseCase:
    def __init__(self, project_repository: ProjectRepository):
        self.project_repository = project_repository

    async def execute(self, tenant_id: uuid.UUID) -> List[Project]:
        return await self.project_repository.get_by_tenant_id(tenant_id)

class GetProjectByIdUseCase:
    def __init__(self, project_repository: ProjectRepository):
        self.project_repository = project_repository

    async def execute(self, project_id: uuid.UUID, tenant_id: uuid.UUID) -> Project | None:
        return await self.project_repository.get_by_id(project_id, tenant_id)

class UpdateProjectUseCase:
    def __init__(self, project_repository: ProjectRepository):
        self.project_repository = project_repository

    async def execute(self, project_id: uuid.UUID, project_data: ProjectCreateDTO, tenant_id: uuid.UUID) -> Project | None:
        # First get the existing project
        project = await self.project_repository.get_by_id(project_id, tenant_id)
        if not project:
            return None
        
        # Update the project with new data
        update_data = project_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(project, key):
                setattr(project, key, value)
        
        # Save the updated project
        updated_project = await self.project_repository.update(project)
        return updated_project

import logging

class DeleteProjectUseCase:
    def __init__(self, project_repository: ProjectRepository):
        self.project_repository = project_repository
        self.logger = logging.getLogger(__name__)

    async def execute(self, project_id: uuid.UUID, tenant_id: uuid.UUID) -> bool:
        """
        Delete a project by ID
        
        Args:
            project_id: The ID of the project to delete
            tenant_id: The ID of the tenant (for authorization)
            
        Returns:
            bool: True if the project was deleted, False if it didn't exist or access denied
        """
        try:
            self.logger.info(f"[DeleteProjectUseCase] Starting deletion of project {project_id} for tenant {tenant_id}")
            result = await self.project_repository.delete(project_id, tenant_id)
            if result:
                self.logger.info(f"[DeleteProjectUseCase] Successfully deleted project {project_id}")
            else:
                self.logger.warning(f"[DeleteProjectUseCase] Project {project_id} not found or access denied")
            return result
        except Exception as e:
            self.logger.error(f"[DeleteProjectUseCase] Error deleting project {project_id}: {str(e)}", exc_info=True)
            raise

class CreateTaskUseCase:
    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository
        
    async def execute(self, task_data: TaskCreateDTO, project_id: uuid.UUID) -> Task:
        # Create a new task with required fields
        task = Task(
            title=task_data.title,
            description=task_data.description or "",
            status=task_data.status or "todo",
            project_id=project_id,
            created_at=datetime.utcnow()
        )
        
        try:
            await self.task_repository.add(task)
            # Get the created task with all fields populated
            created_task = await self.task_repository.get_by_id(task.id)
            return created_task
        except Exception as e:
            logging.error(f"Failed to create task: {str(e)}")
            raise

class GetTasksByProjectUseCase:
    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository

    async def execute(self, project_id: uuid.UUID) -> List[Task]:
        return await self.task_repository.get_by_project_id(project_id)

class UpdateTaskUseCase:
    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository

    async def execute(self, task_id: uuid.UUID, task_data: TaskUpdateDTO) -> Task | None:
        # Get the existing task from the repository
        task = await self.task_repository.get_by_id(task_id)
        if not task:
            return None
        
        # Create a new Task instance with the updated values
        update_data = task_data.model_dump(exclude_unset=True)
        
        # Only update fields that were provided in the DTO
        updated_task = Task(
            id=task.id,
            project_id=task.project_id,
            title=update_data.get('title', task.title),
            description=update_data.get('description', task.description),
            status=update_data.get('status', task.status),
            assignee_id=update_data.get('assignee_id', task.assignee_id),
            created_at=task.created_at,
            due_date=update_data.get('due_date', task.due_date) if 'due_date' in update_data else task.due_date
        )
        
        try:
            # Update the task in the repository
            await self.task_repository.update(updated_task)
            
            # Return the updated task
            return await self.task_repository.get_by_id(task_id)
        except Exception as e:
            # Log the error for debugging
            import logging
            logging.error(f"Error updating task {task_id}: {str(e)}")
            raise ValueError(f"Failed to update task: {str(e)}")

class DeleteTaskUseCase:
    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository

    async def execute(self, task_id: uuid.UUID) -> bool:
        """
        Delete a task by ID
        
        Args:
            task_id: The ID of the task to delete
            
        Returns:
            bool: True if the task was deleted, False if it didn't exist
        """
        # First check if task exists
        task = await self.task_repository.get_by_id(task_id)
        if not task:
            return False
            
        # Delete the task
        await self.task_repository.delete(task_id)
        return True
