import pytest
from fastapi import status
from sqlalchemy import select
from application.dtos import UserCreateDTO, UserDTO
from infrastructure.models import UserModel

# Test user registration
async def test_register_user(client, db_session):
    session, _, _, _ = db_session
    
    # First, delete the test user if it exists
    result = await session.execute(select(UserModel).where(UserModel.email == "newuser@example.com"))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        await session.delete(existing_user)
        await session.commit()
    
    # Test data for registration
    user_data = {
        "email": "newuser@example.com",
        "password": "testpass123",
        "username": "newuser",
        "tenant_name": "New Test Tenant",
        "tenant_domain": "new-test-tenant.local"
    }
    
    # Register new user using the /api/register endpoint
    response = await client.post("/api/register", json=user_data)
    
    # Check response - API returns 200 OK on successful registration
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "id" in data
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert "hashed_password" not in data  # Password should not be returned
    
    # Verify user was created in database
    result = await session.execute(select(UserModel).where(UserModel.email == user_data["email"]))
    db_user = result.scalar_one_or_none()
    assert db_user is not None
    assert db_user.email == user_data["email"]
    assert db_user.username == user_data["username"]

# Test login with valid credentials
async def test_login_valid_credentials(client, test_user):
    login_data = {
        "username": test_user.email,
        "password": "testpass123"
    }
    
    # Use form data for login as expected by the API
    # Login endpoint is at /api/token
    # Use OAuth2 password flow format
    form_data = {
        "username": login_data["username"],
        "password": login_data["password"],
        "grant_type": "password"
    }
    response = await client.post("/api/token", 
                              data=form_data,
                              headers={"Content-Type": "application/x-www-form-urlencoded"})
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"

# Test login with invalid credentials
async def test_login_invalid_credentials(client, test_user):
    login_data = {
        "username": test_user.email,
        "password": "wrongpassword"
    }
    
    # Use form data for login as expected by the API
    # Login endpoint is at /api/token
    # Use OAuth2 password flow format
    form_data = {
        "username": login_data["username"],
        "password": login_data["password"],
        "grant_type": "password"
    }
    response = await client.post("/api/token", 
                              data=form_data,
                              headers={"Content-Type": "application/x-www-form-urlencoded"})
    
    # Print response for debugging
    print(f"Response status: {response.status_code}")
    print(f"Response content: {response.text}")
    
    # Check the response status code
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Check if the response is JSON
    if response.headers.get("content-type") == "application/json":
        error_data = response.json()
        if "detail" in error_data:
            error_message = str(error_data["detail"]).lower()
            assert any(msg in error_message for msg in ["invalid", "incorrect", "not found"])
    else:
        # If not JSON, check for error message in text
        assert any(msg in response.text.lower() for msg in ["invalid", "incorrect", "not found"])

# Test getting current user with valid token
# Note: The /me endpoint might not be implemented in the API yet
# We'll test the token generation and validation instead
async def test_token_generation(client, test_user):
    # First get a token
    form_data = {
        "username": test_user.email,
        "password": "testpass123",
        "grant_type": "password"
    }
    
    # Login endpoint is at /api/token
    response = await client.post(
        "/api/token",
        data=form_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    # Check the response
    assert response.status_code == status.HTTP_200_OK
    token_data = response.json()
    
    # Verify the token structure
    assert "access_token" in token_data
    assert "token_type" in token_data
    assert token_data["token_type"] == "bearer"
    
    # Verify it's a valid JWT token (3 parts separated by dots)
    token_parts = token_data["access_token"].split(".")
    assert len(token_parts) == 3, "JWT token should have 3 parts"

# Test login with invalid credentials
async def test_login_with_invalid_credentials(client):
    # Try to login with invalid credentials
    form_data = {
        "username": "nonexistent@example.com",
        "password": "wrongpassword",
        "grant_type": "password"
    }
    response = await client.post(
        "/api/token",
        data=form_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    # Print response for debugging
    print(f"Response status: {response.status_code}")
    print(f"Response content: {response.text}")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Check if the response is JSON
    if response.headers.get("content-type") == "application/json":
        error_data = response.json()
        if "detail" in error_data:
            error_message = str(error_data["detail"]).lower()
            assert any(msg in error_message for msg in ["no user found", "invalid", "incorrect"])
    else:
        # If not JSON, check for error message in text
        assert any(msg in response.text.lower() for msg in ["no user found", "invalid", "incorrect"]) or "Incorrect email or password" in response.text
