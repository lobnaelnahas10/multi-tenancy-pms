import pytest
import uuid
from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from application.dtos import ProjectCreateDTO
from infrastructure.models import ProjectModel, ProjectUserModel, UserModel

# Test data
TEST_PASSWORD = "testpass123"

# Test creating a project
async def test_create_project(auth_client, db_session):
    # Unpack the db_session tuple
    session, test_user, test_project, test_task = db_session
    
    # Create test project data with only the fields expected by ProjectCreateDTO
    project_data = {
        "name": "New Test Project",
        "description": "A new test project"
    }
    
    # Make the API request
    response = await auth_client.post("/api/projects/", json=project_data)
    
    # Verify the response
    assert response.status_code == status.HTTP_201_CREATED, f"Expected 201, got {response.status_code}: {response.text}"
    data = response.json()
    assert "id" in data, "Response missing 'id' field"
    assert data["name"] == project_data["name"], f"Expected name {project_data['name']}, got {data['name']}"
    assert data["description"] == project_data["description"], f"Expected description {project_data['description']}, got {data['description']}"
    
    # Verify project was created in database
    result = await session.execute(select(ProjectModel).where(ProjectModel.name == "New Test Project"))
    db_project = result.scalars().first()
    assert db_project is not None, "Project not found in database"
    assert str(db_project.id) == data["id"], "Project ID mismatch"
    assert db_project.name == project_data["name"], "Project name mismatch"
    assert db_project.description == project_data["description"], "Project description mismatch"
    
    # Verify project user association was created
    result = await session.execute(
        select(ProjectUserModel)
        .where(ProjectUserModel.project_id == db_project.id)
        .where(ProjectUserModel.user_id == test_user.id)
    )
    project_user = result.scalars().first()
    
    # If no project_user found, let's see what's in the project_users table
    if project_user is None:
        all_project_users = await session.execute(select(ProjectUserModel))
        all_project_users = all_project_users.scalars().all()
        print(f"All project users in database: {all_project_users}")
        
    assert project_user is not None, (
        f"Project-User association not found for project {db_project.id} and user {test_user.id}. "
        f"Project ID type: {type(db_project.id)}, User ID type: {type(test_user.id)}"
    )
    assert project_user.role == "owner", f"Expected role 'owner', got {project_user.role}"

# Test getting a project
async def test_get_project(auth_client, test_project):
    response = await auth_client.get(f"/api/projects/{test_project.id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(test_project.id)
    assert data["name"] == test_project.name
    assert data["description"] == test_project.description

# Test updating a project
async def test_update_project(auth_client, test_project):
    update_data = {
        "name": "Updated Project Name",
        "description": "Updated description"
    }
    
    response = await auth_client.patch(
        f"/api/projects/{test_project.id}",
        json=update_data
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]

# Test deleting a project
async def test_delete_project(auth_client, test_project, db_session):
    session, _, _, _ = db_session
    
    # First, verify the project exists
    result = await session.execute(
        select(ProjectModel).where(ProjectModel.id == test_project.id)
    )
    assert result.scalar_one_or_none() is not None
    
    # Delete the project
    response = await auth_client.delete(f"/api/projects/{test_project.id}")
    assert response.status_code == status.HTTP_200_OK
    
    # Verify the project was deleted
    result = await session.execute(
        select(ProjectModel).where(ProjectModel.id == test_project.id)
    )
    assert result.scalar_one_or_none() is None

# Test listing projects
async def test_list_projects(auth_client, test_project):
    response = await auth_client.get("/api/projects/")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(p["id"] == str(test_project.id) for p in data)

# Test unauthorized access to projects
async def test_unauthorized_project_access(client, test_project):
    # Try to access projects without authentication
    response = await client.get("/api/projects/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Try to access a specific project without authentication
    response = await client.get(f"/api/projects/{test_project.id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

# Test updating non-existent project
async def test_update_nonexistent_project(auth_client):
    non_existent_id = uuid.uuid4()
    update_data = {
        "name": "Updated Project",
        "description": "This project doesn't exist"
    }
    
    response = await auth_client.patch(
        f"/api/projects/{non_existent_id}",
        json=update_data
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND

# Test deleting non-existent project
async def test_delete_nonexistent_project(auth_client):
    non_existent_id = uuid.uuid4()
    response = await auth_client.delete(f"/api/projects/{non_existent_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND

# Test creating project with invalid data
async def test_create_project_invalid_data(auth_client):
    # Missing required field 'name'
    invalid_data = {
        "description": "Project with no name"
    }
    response = await auth_client.post("/api/projects/", json=invalid_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

# Test updating project with empty name
async def test_update_project_empty_name(auth_client, test_project):
    # Empty name is allowed by the API
    update_data = {
        "name": "",
        "description": "Updated description"
    }
    response = await auth_client.patch(
        f"/api/projects/{test_project.id}",
        json=update_data
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == ""  # Empty string is allowed

# Test getting non-existent project
async def test_get_nonexistent_project(auth_client):
    non_existent_id = uuid.uuid4()
    response = await auth_client.get(f"/api/projects/{non_existent_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND

# Test creating project with same name
async def test_create_project_same_name(auth_client, test_project):
    # The API allows projects with the same name
    duplicate_data = {
        "name": test_project.name,
        "description": "Project with same name"
    }
    response = await auth_client.post("/api/projects/", json=duplicate_data)
    assert response.status_code == status.HTTP_201_CREATED  # Duplicate names are allowed
    data = response.json()
    assert data["name"] == test_project.name
