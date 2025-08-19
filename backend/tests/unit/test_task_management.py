import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
import pytest_asyncio
from datetime import datetime

from domain.entities import Task, User, Project
from application.use_cases.task_management import TaskManagementUseCase
from application.dtos import TaskCreateDTO, TaskUpdateDTO

# Fixtures
@pytest_asyncio.fixture
async def task_management_use_case():
    """Fixture for TaskManagementUseCase with mocked dependencies."""
    task_repo = AsyncMock()
    user_repo = AsyncMock()
    project_repo = AsyncMock()
    
    return TaskManagementUseCase(
        task_repository=task_repo,
        user_repository=user_repo,
        project_repository=project_repo
    )

@pytest.fixture
def test_user():
    """Fixture for a test user."""
    return User(
        id=uuid4(),
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
        tenant_id=uuid4(),
        role="user"
    )

@pytest.fixture
def test_project(test_user):
    """Fixture for a test project."""
    return Project(
        id=uuid4(),
        name="Test Project",
        description="Test Description",
        created_by=test_user.id,
        tenant_id=test_user.tenant_id
    )

@pytest.fixture
def test_task(test_project, test_user):
    """Fixture for a test task."""
    return Task(
        id=uuid4(),
        title="Test Task",
        description="Test Description",
        status="todo",
        project_id=test_project.id,
        created_by=test_user.id,
        created_at=datetime.utcnow()
    )

# Test cases
class TestTaskManagementUseCase:
    async def test_create_task_success(self, task_management_use_case, test_user, test_project):
        # Setup
        task_data = TaskCreateDTO(
            title="New Task",
            description="Task Description",
            status="todo"
        )
        
        # Mock project repository to return a project
        task_management_use_case.project_repository.get_by_id = AsyncMock(return_value=test_project)
        
        # Mock task repository
        created_task = Task(
            id=uuid4(),
            title=task_data.title,
            description=task_data.description,
            status=task_data.status,
            project_id=test_project.id,
            created_by=test_user.id,
            tenant_id=test_user.tenant_id
        )
        task_management_use_case.task_repository.add = AsyncMock(return_value=created_task)
        
        # Execute
        result = await task_management_use_case.create_task(
            project_id=test_project.id,
            task_data=task_data,
            current_user=test_user
        )
        
        # Assert
        assert result is not None
        assert result.title == task_data.title
        assert result.description == task_data.description
        assert result.status == task_data.status
        task_management_use_case.project_repository.get_by_id.assert_called_once_with(test_project.id, test_user.tenant_id)
        task_management_use_case.task_repository.add.assert_called_once()

    async def test_create_task_project_not_found(self, task_management_use_case, test_user):
        # Setup
        task_data = TaskCreateDTO(
            title="New Task",
            description="Task Description",
            status="todo"  # Adding required status field
        )
        
        # Mock project repository to return None (project not found)
        task_management_use_case.project_repository.get_by_id = AsyncMock(return_value=None)
        
        # Execute & Assert
        with pytest.raises(ValueError, match="Project not found or access denied"):
            await task_management_use_case.create_task(
                project_id=uuid4(),
                task_data=task_data,
                current_user=test_user
            )

    async def test_update_task_success(self, task_management_use_case, test_user, test_project, test_task):
        # Setup
        updates = TaskUpdateDTO(
            title="Updated Task",
            description="Updated Description",
            status="in_progress"
        )
        
        # Mock task repository
        task_management_use_case.task_repository.get_by_id = AsyncMock(return_value=test_task)
        task_management_use_case.project_repository.get_by_id = AsyncMock(return_value=test_project)
        
        # Mock the update to return the updated task
        updated_task = Task(**{**test_task.__dict__, **updates.model_dump(exclude_unset=True)})
        task_management_use_case.task_repository.update = AsyncMock(return_value=updated_task)
        
        # Execute
        result = await task_management_use_case.update_task(
            task_id=test_task.id,
            updates=updates,
            current_user=test_user
        )
        
        # Assert
        assert result is not None
        assert result.title == updates.title
        assert result.description == updates.description
        assert result.status == updates.status
        task_management_use_case.task_repository.update.assert_called_once()

    async def test_delete_task_success(self, task_management_use_case, test_user, test_project, test_task):
        # Setup
        task_management_use_case.task_repository.get_by_id = AsyncMock(return_value=test_task)
        task_management_use_case.project_repository.get_by_id = AsyncMock(return_value=test_project)
        task_management_use_case.task_repository.delete = AsyncMock(return_value=True)
        
        # Execute
        result = await task_management_use_case.delete_task(
            task_id=test_task.id,
            current_user=test_user
        )
        
        # Assert
        assert result is True
        task_management_use_case.task_repository.delete.assert_called_once_with(test_task.id)

    async def test_get_task_success(self, task_management_use_case, test_user, test_project, test_task):
        # Setup
        task_management_use_case.task_repository.get_by_id = AsyncMock(return_value=test_task)
        task_management_use_case.project_repository.get_by_id = AsyncMock(return_value=test_project)
        
        # Execute
        result = await task_management_use_case.get_task(
            task_id=test_task.id,
            current_user=test_user
        )
        
        # Assert
        assert result is not None
        assert result.id == test_task.id
        assert result.title == test_task.title
        task_management_use_case.task_repository.get_by_id.assert_called_once_with(test_task.id)

    async def test_get_project_tasks_success(self, task_management_use_case, test_user, test_project, test_task):
        # Setup
        task_management_use_case.project_repository.get_by_id = AsyncMock(return_value=test_project)
        task_management_use_case.task_repository.get_by_project_id = AsyncMock(return_value=[test_task])
        
        # Execute
        result = await task_management_use_case.get_project_tasks(
            project_id=test_project.id,
            current_user=test_user
        )
        
        # Assert
        assert len(result) == 1
        assert result[0].id == test_task.id
        task_management_use_case.task_repository.get_by_project_id.assert_called_once_with(test_project.id)

    async def test_validate_assignee_success(self, task_management_use_case, test_user):
        # Setup
        assignee = User(
            id=uuid4(),
            username="assignee",
            email="assignee@example.com",
            hashed_password="hashed",
            tenant_id=test_user.tenant_id,
            role="user"
        )
        task_management_use_case.user_repository.get_by_id = AsyncMock(return_value=assignee)
        
        # Execute - should not raise an exception
        await task_management_use_case._validate_assignee(assignee.id, test_user.tenant_id)
        
        # Assert
        task_management_use_case.user_repository.get_by_id.assert_called_once_with(assignee.id)

    async def test_validate_assignee_not_found(self, task_management_use_case, test_user):
        # Setup
        task_management_use_case.user_repository.get_by_id = AsyncMock(return_value=None)
        
        # Execute & Assert
        with pytest.raises(ValueError, match="Invalid assignee"):
            await task_management_use_case._validate_assignee(uuid4(), test_user.tenant_id)

    async def test_validate_assignee_wrong_tenant(self, task_management_use_case, test_user):
        # Setup
        assignee = User(
            id=uuid4(),
            username="other_tenant_user",
            email="other@example.com",
            hashed_password="hashed",
            tenant_id=uuid4(),  # Different tenant
            role="user"
        )
        task_management_use_case.user_repository.get_by_id = AsyncMock(return_value=assignee)
        
        # Execute & Assert
        with pytest.raises(ValueError, match="Invalid assignee"):
            await task_management_use_case._validate_assignee(assignee.id, test_user.tenant_id)
