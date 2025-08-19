import asyncio
import platform
import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from core.config import settings

# Fix for Windows event loop
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_projects_table():
    # Create an async engine
    engine = create_async_engine(settings.DATABASE_URL)
    
    # Create an async session
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    
    async with async_session() as session:
        try:
            # Check if the projects table exists and has the updated_at column
            result = await session.execute(
                text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = 'projects';
                """)
            )
            
            columns = result.fetchall()
            logger.info("Current columns in 'projects' table:")
            for col in columns:
                logger.info(f"- {col[0]}: {col[1]}, Nullable: {col[2]}, Default: {col[3]}")
            
            # Check if updated_at column exists
            updated_at_exists = any(col[0] == 'updated_at' for col in columns)
            
            if not updated_at_exists:
                logger.info("Adding 'updated_at' column to 'projects' table...")
                await session.execute(
                    text("""
                    ALTER TABLE projects
                    ADD COLUMN updated_at TIMESTAMP WITHOUT TIME ZONE 
                    DEFAULT (now() AT TIME ZONE 'utc')
                    NOT NULL;
                    """)
                )
                await session.commit()
                logger.info("Successfully added 'updated_at' column to 'projects' table")
            else:
                logger.info("'updated_at' column already exists in 'projects' table")
                
        except Exception as e:
            logger.error(f"Error checking/updating database: {str(e)}")
            await session.rollback()
            raise
        finally:
            await session.close()

if __name__ == "__main__":
    try:
        asyncio.run(check_projects_table())
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise
