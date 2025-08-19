from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database import get_db
from infrastructure.repositories import (
    UserRepositoryImpl, TenantRepositoryImpl, ProjectRepositoryImpl, TaskRepositoryImpl
)
from infrastructure.project_user_repository import ProjectUserRepositoryImpl
from domain.repositories import (
    UserRepository, TenantRepository, ProjectRepository, TaskRepository, ProjectUserRepository
)
from application.use_cases.user_management import RegisterUserUseCase, AuthenticateUserUseCase
from application.use_cases.project_management import (
    CreateProjectUseCase, GetProjectsByTenantUseCase, GetProjectByIdUseCase, 
    UpdateProjectUseCase, DeleteProjectUseCase, CreateTaskUseCase, 
    GetTasksByProjectUseCase, UpdateTaskUseCase, DeleteTaskUseCase
)
from application.use_cases.project_user_management import GetProjectUsersUseCase

def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepositoryImpl(db)

def get_tenant_repository(db: AsyncSession = Depends(get_db)) -> TenantRepository:
    return TenantRepositoryImpl(db)

def get_project_repository(db: AsyncSession = Depends(get_db)) -> ProjectRepository:
    return ProjectRepositoryImpl(db)

def get_task_repository(db: AsyncSession = Depends(get_db)) -> TaskRepository:
    return TaskRepositoryImpl(db)

def get_project_user_repository(db: AsyncSession = Depends(get_db)) -> ProjectUserRepository:
    return ProjectUserRepositoryImpl(db)

def get_register_user_use_case(
    user_repo: UserRepository = Depends(get_user_repository),
    tenant_repo: TenantRepository = Depends(get_tenant_repository)
) -> RegisterUserUseCase:
    return RegisterUserUseCase(user_repo, tenant_repo)

def get_authenticate_user_use_case(
    user_repo: UserRepository = Depends(get_user_repository)
) -> AuthenticateUserUseCase:
    return AuthenticateUserUseCase(user_repo)

# Project Use Case Dependencies
def get_create_project_use_case(
    project_repo: ProjectRepository = Depends(get_project_repository),
    project_user_repo: ProjectUserRepository = Depends(get_project_user_repository)
) -> CreateProjectUseCase:
    return CreateProjectUseCase(project_repo, project_user_repo)

def get_projects_by_tenant_use_case(
    project_repo: ProjectRepository = Depends(get_project_repository)
) -> GetProjectsByTenantUseCase:
    return GetProjectsByTenantUseCase(project_repo)

def get_project_by_id_use_case(
    project_repo: ProjectRepository = Depends(get_project_repository)
) -> GetProjectByIdUseCase:
    return GetProjectByIdUseCase(project_repo)

def get_delete_project_use_case(
    project_repo: ProjectRepository = Depends(get_project_repository)
) -> DeleteProjectUseCase:
    return DeleteProjectUseCase(project_repo)

def get_update_project_use_case(
    project_repo: ProjectRepository = Depends(get_project_repository)
) -> UpdateProjectUseCase:
    return UpdateProjectUseCase(project_repo)

# Task Use Case Dependencies
def get_create_task_use_case(
    task_repo: TaskRepository = Depends(get_task_repository)
) -> CreateTaskUseCase:
    return CreateTaskUseCase(task_repo)

def get_tasks_by_project_use_case(
    task_repo: TaskRepository = Depends(get_task_repository)
) -> GetTasksByProjectUseCase:
    return GetTasksByProjectUseCase(task_repo)

def get_update_task_use_case(
    task_repo: TaskRepository = Depends(get_task_repository)
) -> UpdateTaskUseCase:
    return UpdateTaskUseCase(task_repo)

def get_delete_task_use_case(
    task_repo: TaskRepository = Depends(get_task_repository)
) -> DeleteTaskUseCase:
    return DeleteTaskUseCase(task_repo)

def get_project_users_use_case(
    project_user_repo: ProjectUserRepository = Depends(get_project_user_repository)
) -> GetProjectUsersUseCase:
    return GetProjectUsersUseCase(project_user_repo)
