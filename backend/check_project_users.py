import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import uuid

# Import models after setting up the environment
load_dotenv()
from infrastructure.models import ProjectUserModel, UserModel

async def check_project_users():
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        print("Error: DATABASE_URL not found in environment variables")
        return
        
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    
    project_id = 'fdf9b0b3-ef6f-4685-bff6-27ad1bb1a62c'
    
    async with async_session() as session:
        try:
            # Check if project exists in project_users
            stmt = select(ProjectUserModel).where(ProjectUserModel.project_id == project_id)
            result = await session.execute(stmt)
            project_users = result.scalars().all()
            
            print(f'Found {len(project_users)} project users for project {project_id}')
            
            if not project_users:
                print("No users found for this project. Checking if project exists...")
                # Check if project exists in projects table
                from infrastructure.models import ProjectModel
                project_stmt = select(ProjectModel).where(ProjectModel.id == project_id)
                project_result = await session.execute(project_stmt)
                project = project_result.scalar_one_or_none()
                if project:
                    print(f"Project exists: {project.name} (ID: {project.id})")
                else:
                    print(f"Project with ID {project_id} does not exist")
            
            for pu in project_users:
                print(f'Project User: project_id={pu.project_id}, user_id={pu.user_id}, role={pu.role}')
                # Get user details
                user_stmt = select(UserModel).where(UserModel.id == pu.user_id)
                user_result = await session.execute(user_stmt)
                user = user_result.scalar_one_or_none()
                if user:
                    print(f'  User: id={user.id}, username={user.username}, email={user.email}')
                else:
                    print('  User not found')
                    
        except Exception as e:
            print(f"Error: {str(e)}")
            
        await session.close()
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_project_users())
