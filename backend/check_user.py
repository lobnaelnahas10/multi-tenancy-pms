import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from infrastructure.models import Base, UserModel

async def check_user(email, password):
    DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/pms"
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        # Create a session
        async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
        
        async with async_session() as session:
            # Find user by email
            result = await session.execute(
                select(UserModel).where(UserModel.email == email)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                print(f"No user found with email: {email}")
                return
                
            print(f"User found: {user.email}")
            print(f"Hashed password: {user.hashed_password}")
            print(f"User role: {user.role}")
            print(f"Tenant ID: {user.tenant_id}")
            
            # Verify the password
            from application.services import PasswordService
            is_valid = PasswordService.verify_password(password, user.hashed_password)
            print(f"Password valid: {is_valid}")

if __name__ == "__main__":
    email = "l@x.com"
    password = "12345678"
    asyncio.run(check_user(email, password))
