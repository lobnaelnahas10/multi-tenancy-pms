import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def check_database():
    # Get database URL from environment variables
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("Error: DATABASE_URL not found in .env file")
        return
    
    try:
        # Parse the database URL
        # Format: postgresql+asyncpg://user:password@host:port/dbname
        db_url_parts = database_url.split('//')[1].split('@')
        user_pass = db_url_parts[0].split(':')
        host_port_db = db_url_parts[1].split('/')
        host_port = host_port_db[0].split(':')
        
        db_params = {
            'user': user_pass[0],
            'password': user_pass[1].split('@')[0],
            'database': host_port_db[1],
            'host': host_port[0],
            'port': int(host_port[1]) if len(host_port) > 1 else 5432
        }
        
        # Connect to the database
        conn = await asyncpg.connect(**db_params)
        
        # Check if project_users table exists
        exists = await conn.fetchval(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'project_users'
            );
            """
        )
        
        print(f"Project Users Table Exists: {exists}")
        
        # List all tables
        tables = await conn.fetch(
            """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
            """
        )
        
        print("\nExisting Tables:")
        for table in tables:
            print(f"- {table['table_name']}")
        
        # Check if the table needs to be created
        if not exists:
            print("\nCreating project_users table...")
            await conn.execute("""
                CREATE TABLE project_users (
                    project_id UUID NOT NULL,
                    user_id UUID NOT NULL,
                    role VARCHAR NOT NULL DEFAULT 'member',
                    joined_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() AT TIME ZONE 'utc') NOT NULL,
                    PRIMARY KEY (project_id, user_id),
                    FOREIGN KEY(project_id) REFERENCES projects (id) ON DELETE CASCADE,
                    FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
                );
                
                CREATE INDEX ix_project_users_project_id ON project_users (project_id);
                CREATE INDEX ix_project_users_user_id ON project_users (user_id);
            """)
            print("Successfully created project_users table")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_database())
