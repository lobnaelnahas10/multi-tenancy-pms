import pytest
import uuid
from fastapi import status
from sqlalchemy import select
from application.dtos import TaskCreateDTO, TaskUpdateDTO
from infrastructure.models import TaskModel

# Test creating a task
async def test_create_task(auth_client, db_session, test_project):
    session, test_user, _, _ = db_session
    
    task_data = {
        "title": "New Test Task",
        "description": "A new test task",
        "status": "todo"
    }
    
    # Create task using the API
    response = await auth_client.post(f"/api/projects/{test_project.id}/tasks/", json=task_data)
    
    # Check response
    assert response.status_code == status.HTTP_201_CREATED, f"Expected 201, got {response.status_code}: {response.text}"
    data = response.json()
    
    # Verify response data
    assert "id" in data
    assert data["title"] == task_data["title"]
    assert data["description"] == task_data["description"]
    assert data["status"] == task_data["status"]
    assert "created_at" in data
    
    # Verify task was created in database
    result = await session.execute(select(TaskModel).where(TaskModel.id == uuid.UUID(data["id"])))
    task = result.scalar_one_or_none()
    assert task is not None, "Task was not created in the database"
    assert task.title == task_data["title"]
    assert task.description == task_data["description"]
    assert task.status == task_data["status"]
    assert str(task.project_id) == str(test_project.id)

# Test getting tasks list (not individual task)
async def test_get_task(auth_client, test_task, test_project):
    # The API only has a list endpoint, not a get by ID endpoint
    response = await auth_client.get(f"/api/projects/{test_project.id}/tasks/")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    # Find our test task in the list
    task = next((t for t in data if t["id"] == str(test_task.id)), None)
    assert task is not None
    assert task["title"] == test_task.title
    assert task["description"] == test_task.description
    assert task["status"] == test_task.status

# Test updating a task
async def test_update_task(auth_client, test_task, test_project, test_user, db_session):
    # Log file for debugging
    log_file = "test_update_task_debug.log"
    
    # Prepare the update payload with valid status value
    update_data = {
        "title": "Updated Task Title",
        "description": "Updated description",
        "status": "todo",  # Using a valid status from Task model
        "assignee_id": str(test_user.id)  # Ensure this is a string UUID
    }
    
    # Log initial test data
    with open(log_file, "w") as f:
        f.write(f"=== Test Update Task Debug Log ===\n")
        f.write(f"Test Project ID: {test_project.id}\n")
        f.write(f"Test Task ID: {test_task.id}\n")
        f.write(f"Test User ID: {test_user.id}\n")
        f.write(f"Update Data: {update_data}\n\n")
    
    print(f"\n=== Test Data ===")
    print(f"Project ID: {test_project.id}")
    print(f"Task ID: {test_task.id}")
    print(f"Update data: {update_data}")
    
    # Send the PATCH request to update the task
    try:
        response = await auth_client.patch(
            f"/api/projects/{test_project.id}/tasks/{test_task.id}",
            json=update_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n=== Response ===")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        # Log response details to file
        with open(log_file, "a") as f:
            f.write(f"\n=== Response ===\n")
            f.write(f"Status: {response.status_code}\n")
            f.write(f"Headers: {dict(response.headers)}\n")
            f.write("\n=== Response Content ===\n")
            
            # Try to get response text
            try:
                response_text = response.text
                f.write(f"{response_text}\n")
            except Exception as e:
                f.write(f"Could not get response text: {e}\n")
            
            # Try to parse as JSON
            try:
                json_data = response.json()
                f.write("\n=== Parsed JSON ===\n")
                import json
                f.write(json.dumps(json_data, indent=2) + "\n")
            except Exception as e:
                f.write(f"\nCould not parse response as JSON: {e}\n")
            
            # Log raw content as hex if text decoding fails
            try:
                if not response_text.strip() and response.content:
                    f.write("\n=== Raw Content (hex) ===\n")
                    f.write(response.content.hex() + "\n")
            except:
                pass
        
        # Print a message about the log file
        print(f"\n=== Debug information has been written to {log_file} ===")
        
        # For the test output, just show a summary
        if response.status_code != status.HTTP_200_OK:
            print(f"Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print("Could not parse error details. Check the log file for more information.")
        
        # Verify the response
        assert response.status_code == status.HTTP_200_OK, \
            f"Expected 200 OK, got {response.status_code}: {response.text}"
        
        # Verify the response data
        updated_task = response.json()
        assert updated_task["id"] == str(test_task.id)
        assert updated_task["title"] == update_data["title"]
        assert updated_task["description"] == update_data["description"]
        assert updated_task["status"] == update_data["status"]
        assert updated_task["assignee_id"] == update_data["assignee_id"]
        
        # Verify the update in the database
        session, _, _, _ = db_session
        from sqlalchemy import select
        from infrastructure.models import TaskModel
        
        # Ensure all changes are committed to the database
        await session.commit()
        
        # Query the task directly
        stmt = select(TaskModel).where(TaskModel.id == test_task.id)
        result = await session.execute(stmt)
        db_task = result.scalar_one_or_none()
        
        assert db_task is not None, "Task not found in database"
        assert str(db_task.id) == str(test_task.id), f"Expected task ID {test_task.id}, got {db_task.id}"
        assert db_task.title == update_data["title"], f"Expected title '{update_data['title']}', got '{db_task.title}'"
        assert db_task.description == update_data["description"], f"Expected description '{update_data['description']}', got '{db_task.description}'"
        assert db_task.status == update_data["status"], f"Expected status '{update_data['status']}', got '{db_task.status}'"
        assert str(db_task.assignee_id) == update_data["assignee_id"], f"Expected assignee_id '{update_data['assignee_id']}', got '{db_task.assignee_id}'"
        
    except Exception as e:
        print(f"\n=== Exception during test ===")
        print(f"Type: {type(e).__name__}")
        print(f"Message: {str(e)}")
        raise

# Test deleting a task
async def test_delete_task(auth_client, test_task, test_project, db_session):
    session, _, _, _ = db_session
    
    # First, verify the task exists
    result = await session.execute(
        select(TaskModel).where(TaskModel.id == test_task.id)
    )
    assert result.scalar_one_or_none() is not None
    
    # Delete the task with project_id in the URL
    response = await auth_client.delete(f"/api/projects/{test_project.id}/tasks/{test_task.id}")
    # The API returns 200 OK with a success message
    assert response.status_code == status.HTTP_200_OK
    
    # Verify the task was deleted
    result = await session.execute(
        select(TaskModel).where(TaskModel.id == test_task.id)
    )
    assert result.scalar_one_or_none() is None

# Test listing tasks
async def test_list_tasks(auth_client, test_task, test_project):
    # Use async client with await and include project_id in the URL path
    response = await auth_client.get(f"/api/projects/{test_project.id}/tasks/")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(t["id"] == str(test_task.id) for t in data)

# Test updating task status
async def test_update_task_status(auth_client, test_task, test_project, test_user):
    # First, get the current task to preserve existing values
    response = await auth_client.get(f"/api/projects/{test_project.id}/tasks/")
    assert response.status_code == status.HTTP_200_OK
    tasks = response.json()
    current_task = next((t for t in tasks if t["id"] == str(test_task.id)), None)
    assert current_task is not None
    
    # Create a dictionary with values that match the TaskUpdateDTO
    # Ensure we use the test_user's ID for the assignee_id
    update_dict = {
        "status": "in_progress",
        "title": current_task["title"],  # Keep existing title
        "description": current_task["description"],  # Keep existing description
        "assignee_id": str(test_user.id)  # Ensure this is the same user as in the test data
    }
    
    # Store the expected values for assertions
    expected_assignee_id = str(test_user.id)
    
    # Debug: Print the request being sent
    print(f"Sending PATCH to: /api/projects/{test_project.id}/tasks/{test_task.id}")
    print(f"Request data: {update_dict}")
    
    # Send PATCH request to update task status
    response = None
    try:
        response = await auth_client.patch(
            f"/api/projects/{test_project.id}/tasks/{test_task.id}",
            json=update_dict
        )
    except Exception as e:
        print(f"Request failed with exception: {str(e)}")
        raise
    
    # Check response
    if response.status_code != status.HTTP_200_OK:
        print(f"Update task status failed with status {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Response content: {response.text}")
    assert response.status_code == status.HTTP_200_OK, f"Expected 200 OK, got {response.status_code}: {response.text}"
    data = response.json()
    
    # Verify response data
    assert data["status"] == "in_progress"
    assert data["id"] == str(test_task.id)
    assert data["title"] == current_task["title"]  # Title should be unchanged
    assert data["assignee_id"] == expected_assignee_id  # Verify assignee was updated

# Test unauthorized access to tasks
async def test_unauthorized_task_access(client, test_task, test_project):
    # Try to access tasks without authentication
    response = await client.get(f"/api/projects/{test_project.id}/tasks/")
    # The API returns 401 for unauthorized access
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

# Test task validation
async def test_task_validation(auth_client, test_project):
    # Test missing required fields - title is required
    response = await auth_client.post(
        f"/api/projects/{test_project.id}/tasks/", 
        json={"description": "Missing title"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Test with valid required fields - should pass
    response = await auth_client.post(
        f"/api/projects/{test_project.id}/tasks/", 
        json={
            "title": "Test Task",
            "status": "todo"  # Valid status
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
