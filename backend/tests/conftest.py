import asyncio
import os
import sys
import uuid
from datetime import datetime, timedelta, timezone
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text
from sqlalchemy.pool import StaticPool

# Import the app after setting up the test environment
os.environ['TESTING'] = '1'
from main import app
from core.config import settings
from infrastructure.database import get_db, AsyncSessionLocal
from infrastructure.models import Base, UserModel, ProjectModel, TaskModel, ProjectUserModel, TenantModel
from application.dtos import UserCreateDTO

# Use SQLite in-memory database for testing
settings.DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Disable SQLAlchemy 2.0 deprecation warnings
os.environ["SQLALCHEMY_SILENCE_UBER_WARNING"] = "1"

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_test_token(user_id: str, email: str = "test@example.com", tenant_id: str = None) -> str:
    """Create a test JWT token for authentication.
    
    Args:
        user_id: The user's ID
        email: The user's email (default: test@example.com)
        tenant_id: The tenant ID (default: same as user_id if not provided)
    """
    if tenant_id is None:
        tenant_id = str(user_id)  # Use user_id as tenant_id if not provided
        
    to_encode = {
        "sub": email,  # Email is used as sub in the token
        "email": email,
        "tenant_id": tenant_id,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

# Create test engine and session
engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=True
)

# Create async session factory
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

# Create test database tables
async def init_test_db(session):
    # Create a test tenant
    test_tenant = TenantModel(
        id=uuid.uuid4(),
        name="Test Tenant",
        domain="test-tenant.local",
        created_at=datetime.now(timezone.utc).replace(tzinfo=None)
    )
    session.add(test_tenant)
    await session.commit()
    await session.refresh(test_tenant)
    
    # Get the test tenant from the database
    result = await session.execute(select(TenantModel).where(TenantModel.id == test_tenant.id))
    test_tenant = result.scalar_one_or_none()
    assert test_tenant is not None
    
    # Create a test user
    hashed_password = pwd_context.hash("testpass123")
    user_id = uuid.uuid4()
    test_user = UserModel(
        id=user_id,
        username="testuser",
        email="test@example.com",
        hashed_password=hashed_password,
        role="admin",
        tenant_id=test_tenant.id,
        created_at=datetime.now(timezone.utc).replace(tzinfo=None)
    )
    session.add(test_user)
    await session.commit()
    await session.refresh(test_user)
    
    # Get the test user from the database
    result = await session.execute(select(UserModel).where(UserModel.id == user_id))
    test_user = result.scalar_one_or_none()
    assert test_user is not None
    
    # Create a test project
    project_id = uuid.uuid4()
    project = ProjectModel(
        id=project_id,
        name="Test Project",
        description="A test project",
        tenant_id=test_tenant.id,
        created_at=datetime.now(timezone.utc).replace(tzinfo=None),
        updated_at=datetime.now(timezone.utc).replace(tzinfo=None)
    )
    session.add(project)
    await session.commit()
    await session.refresh(project)
    
    # Get the test project from the database
    result = await session.execute(select(ProjectModel).where(ProjectModel.id == project_id))
    project = result.scalar_one_or_none()
    assert project is not None
    
    # Create a test task
    task = TaskModel(
        id=uuid.uuid4(),
        project_id=project.id,
        title="Test Task",
        description="A test task",
        status="todo",
        assignee_id=test_user.id,
        created_at=datetime.now(timezone.utc).replace(tzinfo=None),
        due_date=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=7)
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    
    # Add user to project
    project_user = ProjectUserModel(
        project_id=project.id,
        user_id=test_user.id,
        role="owner",
        joined_at=datetime.now(timezone.utc).replace(tzinfo=None)
    )
    session.add(project_user)
    await session.commit()
    
    return test_user, project, task

@pytest.fixture(scope="session")
def event_loop():
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="function")
async def db_session():
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # Create a new session for testing
    session = async_session_factory()
    try:
        # Initialize test data
        test_user, test_project, test_task = await init_test_db(session)
        
        # Override the get_db dependency
        async def override_get_db():
            async with session.begin():
                try:
                    yield session
                except Exception as e:
                    await session.rollback()
                    raise e
        
        # Store the original dependency
        original_dependency = app.dependency_overrides.get(get_db, None)
        app.dependency_overrides[get_db] = override_get_db
        
        yield session, test_user, test_project, test_task
        
        # Clean up
        await session.rollback()
        if original_dependency is not None:
            app.dependency_overrides[get_db] = original_dependency
        else:
            app.dependency_overrides.pop(get_db, None)
        
    finally:
        await session.close()

@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    session, test_user, test_project, test_task = db_session
    
    async def override_get_db():
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()
    
    # Store the original dependency
    original_dependency = app.dependency_overrides.get(get_db, None)
    app.dependency_overrides[get_db] = override_get_db
    
    # Create test client without authentication by default
    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client
    
    # Clean up
    if original_dependency is not None:
        app.dependency_overrides[get_db] = original_dependency
    else:
        app.dependency_overrides.pop(get_db, None)

@pytest.fixture(scope="function")
async def test_user(db_session):
    _, test_user, _, _ = db_session
    return test_user

@pytest.fixture(scope="function")
async def auth_client(client, test_user, db_session):
    # Get the test user with tenant information
    session, _, _, _ = db_session
    result = await session.execute(select(UserModel).where(UserModel.id == test_user.id))
    db_user = result.scalar_one_or_none()
    assert db_user is not None, "Test user not found in database"
    
    # Create a JWT token with the required claims (email and tenant_id)
    token = create_test_token(
        user_id=str(db_user.id),
        email=db_user.email,
        tenant_id=str(db_user.tenant_id)
    )
    
    # Set the authorization header for all requests from this client
    client.headers.update({
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    })
    return client

@pytest.fixture(scope="function")
async def test_project(db_session):
    _, _, test_project, _ = db_session
    return test_project

@pytest.fixture(scope="function")
async def test_task(db_session):
    _, _, _, test_task = db_session
    return test_task
