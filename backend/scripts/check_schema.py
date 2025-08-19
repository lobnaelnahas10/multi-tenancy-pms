import asyncio
import platform
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

async def check_tables():
    # Create async engine
    engine = create_async_engine(DATABASE_URL)
    
    # Create async session
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    
    async with async_session() as session:
        try:
            # Check if project_users table exists
            result = await session.execute(
                text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'project_users'
                );
                """)
            )
            exists = result.scalar()
            print(f"Project Users Table Exists: {exists}")
            
            # List all tables
            result = await session.execute(
                text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
                """)
            )
            print("\nExisting Tables:")
            for row in result:
                print(f"- {row[0]}")
                
        except Exception as e:
            print(f"Error checking schema: {e}")
        finally:
            await session.close()
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_tables())
