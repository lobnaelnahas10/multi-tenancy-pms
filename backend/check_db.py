import asyncio
import platform
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# Set the event loop policy for Windows
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from infrastructure.models import Base, UserModel, TenantModel
from dotenv import load_dotenv
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/pms")

async def check_database():
    logger.info("Starting database check...")
    
    try:
        # Create engine
        engine = create_async_engine(DATABASE_URL, echo=True)
        
        # Create async session
        async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
        
        # Test connection
        async with engine.begin() as conn:
            logger.info("Successfully connected to the database")
            
            # List all tables
            logger.info("Listing all tables in the database:")
            result = await conn.run_sync(lambda conn: conn.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
            tables = [row[0] for row in result.fetchall()]
            logger.info(f"Found tables: {', '.join(tables)}")
            
            # Check if users table exists
            if 'users' in tables:
                logger.info("Users table exists. Listing all users:")
                result = await conn.execute(select(UserModel))
                users = result.scalars().all()
                
                if not users:
                    logger.warning("No users found in the database")
                else:
                    for user in users:
                        logger.info(f"User - ID: {user.id}, Email: {user.email}, Username: {user.username}, Tenant ID: {user.tenant_id}")
            else:
                logger.warning("Users table does not exist")
                
            # Check if tenants table exists
            if 'tenants' in tables:
                logger.info("Tenants table exists. Listing all tenants:")
                result = await conn.execute(select(TenantModel))
                tenants = result.scalars().all()
                
                if not tenants:
                    logger.warning("No tenants found in the database")
                else:
                    for tenant in tenants:
                        logger.info(f"Tenant - ID: {tenant.id}, Name: {tenant.name}, Domain: {tenant.domain}")
            else:
                logger.warning("Tenants table does not exist")
                
    except Exception as e:
        logger.error(f"Error checking database: {str(e)}", exc_info=True)
    finally:
        if 'engine' in locals():
            await engine.dispose()
            logger.info("Database connection closed")

if __name__ == "__main__":
    asyncio.run(check_database())
