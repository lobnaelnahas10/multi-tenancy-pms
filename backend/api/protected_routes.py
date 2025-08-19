import logging
from fastapi import APIRouter, Depends, HTTPException, status
import uuid
from typing import List

from application.dtos import ProjectCreateDTO, ProjectDTO, TaskCreateDTO, TaskDTO, TaskUpdateDTO
from application.use_cases.project_management import (
    CreateProjectUseCase, GetProjectsByTenantUseCase, GetProjectByIdUseCase, 
    UpdateProjectUseCase, DeleteProjectUseCase, CreateTaskUseCase, 
    GetTasksByProjectUseCase, UpdateTaskUseCase, DeleteTaskUseCase
)
from application.use_cases.project_user_management import GetProjectUsersUseCase
from .dependencies import (
    get_create_project_use_case, get_projects_by_tenant_use_case, get_project_by_id_use_case, 
    get_update_project_use_case, get_delete_project_use_case, get_create_task_use_case, 
    get_tasks_by_project_use_case, get_update_task_use_case, get_delete_task_use_case,
    get_project_users_use_case
)
from .security import get_current_user
from domain.entities import User, UserDTO

router = APIRouter()

# Project Endpoints
@router.post("/projects/", response_model=ProjectDTO, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreateDTO,
    create_project_use_case: CreateProjectUseCase = Depends(get_create_project_use_case),
    current_user: User = Depends(get_current_user)
):
    project = await create_project_use_case.execute(
        project_data=project_data, 
        tenant_id=current_user.tenant_id,
        user_id=current_user.id
    )
    return project

@router.get("/projects/", response_model=List[ProjectDTO])
async def get_projects(
    get_projects_use_case: GetProjectsByTenantUseCase = Depends(get_projects_by_tenant_use_case),
    current_user: User = Depends(get_current_user)
):
    projects = await get_projects_use_case.execute(current_user.tenant_id)
    return projects

@router.get("/projects/{project_id}", response_model=ProjectDTO)
async def get_project(
    project_id: uuid.UUID,
    get_project_use_case: GetProjectByIdUseCase = Depends(get_project_by_id_use_case),
    current_user: User = Depends(get_current_user)
):
    project = await get_project_use_case.execute(project_id, current_user.tenant_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project

@router.patch("/projects/{project_id}", response_model=ProjectDTO)
async def update_project(
    project_id: uuid.UUID,
    project_data: ProjectCreateDTO,
    update_project_use_case: UpdateProjectUseCase = Depends(get_update_project_use_case),
    current_user: User = Depends(get_current_user)
):
    # Update project with new data
    updated_project = await update_project_use_case.execute(project_id, project_data, current_user.tenant_id)
    if not updated_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found or access denied")
    
    return updated_project

@router.delete("/projects/{project_id}", status_code=status.HTTP_200_OK)
async def delete_project(
    project_id: uuid.UUID,
    delete_project_use_case: DeleteProjectUseCase = Depends(get_delete_project_use_case),
    current_user: User = Depends(get_current_user)
):
    logger = logging.getLogger(__name__)
    logger.info(f"[DELETE /projects/{project_id}] Starting project deletion for user {current_user.id} in tenant {current_user.tenant_id}")
    
    try:
        # Execute the delete operation
        success = await delete_project_use_case.execute(project_id, current_user.tenant_id)
        
        if not success:
            logger.warning(f"[DELETE /projects/{project_id}] Project not found or access denied")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found or access denied"
            )
            
        logger.info(f"[DELETE /projects/{project_id}] Project deleted successfully")
        return {"status": "success", "message": "Project deleted successfully"}
        
    except HTTPException as he:
        logger.error(f"[DELETE /projects/{project_id}] HTTPException: {str(he.detail)}")
        raise
    except Exception as e:
        logger.error(f"[DELETE /projects/{project_id}] Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the project. Please try again later."
        )


@router.get("/projects/{project_id}/users", response_model=List[UserDTO])
async def get_project_users(
    project_id: uuid.UUID,
    get_project_users_use_case: GetProjectUsersUseCase = Depends(get_project_users_use_case),
    current_user: User = Depends(get_current_user)
):
    try:
        users = await get_project_users_use_case.execute(project_id, current_user.tenant_id)
        return users
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e) or "Failed to fetch project users"
        )


# Task Endpoints
@router.post("/projects/{project_id}/tasks/", response_model=TaskDTO, status_code=status.HTTP_201_CREATED)
async def create_task(
    project_id: uuid.UUID,
    task_data: TaskCreateDTO,
    create_task_use_case: CreateTaskUseCase = Depends(get_create_task_use_case),
    get_project_use_case: GetProjectByIdUseCase = Depends(get_project_by_id_use_case),
    current_user: User = Depends(get_current_user)
):
    project = await get_project_use_case.execute(project_id, current_user.tenant_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    task = await create_task_use_case.execute(task_data, project_id)
    return task

@router.get("/projects/{project_id}/tasks/", response_model=List[TaskDTO])
async def get_tasks(
    project_id: uuid.UUID,
    get_tasks_use_case: GetTasksByProjectUseCase = Depends(get_tasks_by_project_use_case),
    get_project_use_case: GetProjectByIdUseCase = Depends(get_project_by_id_use_case),
    current_user: User = Depends(get_current_user)
):
    project = await get_project_use_case.execute(project_id, current_user.tenant_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    tasks = await get_tasks_use_case.execute(project_id)
    return tasks

@router.patch("/projects/{project_id}/tasks/{task_id}", response_model=TaskDTO)
async def update_task(
    project_id: uuid.UUID,
    task_id: uuid.UUID,
    task_data: TaskUpdateDTO,
    update_task_use_case: UpdateTaskUseCase = Depends(get_update_task_use_case),
    get_project_use_case: GetProjectByIdUseCase = Depends(get_project_by_id_use_case),
    current_user: User = Depends(get_current_user)
):
    # Verify project exists and user has access
    project = await get_project_use_case.execute(project_id, current_user.tenant_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or access denied"
        )
    
    # Update the task
    try:
        task = await update_task_use_case.execute(task_id, task_data)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        return task
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e) or "Failed to update task"
        )

@router.delete("/projects/{project_id}/tasks/{task_id}", status_code=status.HTTP_200_OK)
async def delete_task(
    project_id: uuid.UUID,
    task_id: uuid.UUID,
    delete_task_use_case: DeleteTaskUseCase = Depends(get_delete_task_use_case),
    get_project_use_case: GetProjectByIdUseCase = Depends(get_project_by_id_use_case),
    current_user: User = Depends(get_current_user)
):
    # Verify project exists and user has access
    project = await get_project_use_case.execute(project_id, current_user.tenant_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or access denied"
        )
    
    # Delete the task
    try:
        success = await delete_task_use_case.execute(task_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        return {"status": "success", "message": "Task deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e) or "Failed to delete task"
        )
