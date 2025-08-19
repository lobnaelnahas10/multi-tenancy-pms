from typing import Optional, List
import uuid
from datetime import datetime

from domain.entities import Task, User, Project
from domain.repositories import TaskRepository, UserRepository, ProjectRepository
from application.dtos import TaskCreateDTO, TaskDTO, TaskUpdateDTO

class TaskManagementUseCase:
    def __init__(
        self, 
        task_repository: TaskRepository,
        user_repository: UserRepository,
        project_repository: ProjectRepository
    ):
        self.task_repository = task_repository
        self.user_repository = user_repository
        self.project_repository = project_repository
    
    async def create_task(self, project_id: uuid.UUID, task_data: TaskCreateDTO, current_user: User) -> TaskDTO:
        # Verify project exists and user has access
        project = await self.project_repository.get_by_id(project_id, current_user.tenant_id)
        if not project:
            raise ValueError("Project not found or access denied")
        
        # Create new task
        task = Task(
            project_id=project_id,
            title=task_data.title,
            description=task_data.description,
            status=task_data.status or 'todo',
            assignee_id=task_data.assignee_id
        )
        
        # If assignee_id is provided, verify the user exists and is in the same tenant
        if task_data.assignee_id:
            await self._validate_assignee(task_data.assignee_id, current_user.tenant_id)
        
        await self.task_repository.add(task)
        return TaskDTO.model_validate(task)
    
    async def update_task(
        self, 
        task_id: uuid.UUID, 
        updates: TaskUpdateDTO,
        current_user: User
    ) -> Optional[TaskDTO]:
        # Get the existing task
        task = await self.task_repository.get_by_id(task_id)
        if not task:
            return None
        
        # Verify the task belongs to a project the user has access to
        project = await self.project_repository.get_by_id(task.project_id, current_user.tenant_id)
        if not project:
            return None
        
        # Apply updates
        if updates.title is not None:
            task.title = updates.title
        if updates.description is not None:
            task.description = updates.description
        if updates.status is not None:
            task.status = updates.status
        
        # Handle assignee updates
        if updates.assignee_id is not None:
            if updates.assignee_id:
                await self._validate_assignee(updates.assignee_id, current_user.tenant_id)
                user = await self.user_repository.get_by_id(updates.assignee_id)
                if user:
                    task.assign_to(user)
            else:
                task.unassign()
        
        await self.task_repository.update(task)
        
        # Return updated task
        updated_task = await self.task_repository.get_by_id(task_id)
        return TaskDTO.model_validate(updated_task) if updated_task else None
    
    async def delete_task(self, task_id: uuid.UUID, current_user: User) -> bool:
        # Get the task to verify permissions
        task = await self.task_repository.get_by_id(task_id)
        if not task:
            return False
        
        # Verify the task belongs to a project the user has access to
        project = await self.project_repository.get_by_id(task.project_id, current_user.tenant_id)
        if not project:
            return False
        
        # Delete the task
        return await self.task_repository.delete(task_id)
    
    async def get_task(self, task_id: uuid.UUID, current_user: User) -> Optional[TaskDTO]:
        task = await self.task_repository.get_by_id(task_id)
        if not task:
            return None
        
        # Verify the task belongs to a project the user has access to
        project = await self.project_repository.get_by_id(task.project_id, current_user.tenant_id)
        if not project:
            return None
        
        return TaskDTO.model_validate(task)
    
    async def get_project_tasks(self, project_id: uuid.UUID, current_user: User) -> List[TaskDTO]:
        # Verify the project exists and user has access
        project = await self.project_repository.get_by_id(project_id, current_user.tenant_id)
        if not project:
            return []
        
        tasks = await self.task_repository.get_by_project_id(project_id)
        return [TaskDTO.model_validate(task) for task in tasks]
    
    async def _validate_assignee(self, user_id: uuid.UUID, tenant_id: uuid.UUID) -> None:
        """Verify that the assignee exists and belongs to the same tenant."""
        user = await self.user_repository.get_by_id(user_id)
        if not user or user.tenant_id != tenant_id:
            raise ValueError("Invalid assignee: user not found or access denied")
