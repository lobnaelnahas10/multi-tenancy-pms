import asyncio
import uuid
import os
from datetime import datetime
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from infrastructure.models import TenantModel, UserModel, Base
from application.services import PasswordService

# Load environment variables
load_dotenv()

# Database connection string - update this with your actual database URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/pms")

async def create_test_user():
    # Create async engine and session
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create a test tenant
    tenant_id = uuid.uuid4()
    test_tenant = TenantModel(
        id=tenant_id,
        name="Test Tenant",
        domain="test-tenant",
        created_at=datetime.utcnow()
    )
    
    # Create a test user
    user_id = uuid.uuid4()
    test_user = UserModel(
        id=user_id,
        tenant_id=tenant_id,
        username="testuser",
        email="test@example.com",
        hashed_password=PasswordService.get_password_hash("testpass123"),
        role="admin",
        created_at=datetime.utcnow()
    )
    
    # Add to database
    async with async_session() as session:
        # Check if tenant already exists
        result = await session.execute(select(TenantModel).where(TenantModel.domain == "test-tenant"))
        existing_tenant = result.scalars().first()
        
        if not existing_tenant:
            session.add(test_tenant)
        
        # Check if user already exists
        result = await session.execute(select(UserModel).where(UserModel.email == "test@example.com"))
        existing_user = result.scalars().first()
        
        if not existing_user:
            session.add(test_user)
        
        await session.commit()
    
    print("Test user created successfully!")
    print(f"Email: test@example.com")
    print(f"Password: testpass123")
    print(f"Tenant: test-tenant")

if __name__ == "__main__":
    asyncio.run(create_test_user())
