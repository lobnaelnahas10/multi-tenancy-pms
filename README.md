# Project Management System (PMS)

A comprehensive multi-tenant project management system with user authentication, project management, and task tracking capabilities.

## Features

- **Multi-tenancy**: Each organization gets its own isolated workspace
- **User Authentication**: Secure JWT-based authentication
- **Project Management**: Create, view, update, and delete projects
- **Task Tracking**: Manage tasks within projects
- **Role-based Access Control**: Different permission levels for users
- **Responsive UI**: Built with React and Material-UI
- **RESTful API**: Built with FastAPI and PostgreSQL
- **Async Database Operations**: Using SQLAlchemy 2.0 with async support
- **Database Migrations**: Managed with Alembic

## Tech Stack

### Backend
- Python 3.10+
- FastAPI
- SQLAlchemy 2.0 (async)
- PostgreSQL
- Alembic (migrations)
- JWT Authentication

### Frontend
- React 18
- Material-UI
- React Router
- Axios
- React Hook Form

## Docker Setup

### Prerequisites

- Windows 10/11 64-bit: Pro, Enterprise, or Education (Build 16299+)
- WSL 2 feature enabled (Windows Subsystem for Linux 2)
- 64-bit processor with SLAT (Second Level Address Translation)
- 4GB system RAM (8GB recommended)
- Virtualization enabled in BIOS/UEFI
- Administrator privileges

### Installation Steps

1. **Install WSL 2 (if not already installed)**
   ```powershell
   # Run PowerShell as Administrator
   wsl --install
   ```
   - Restart your computer when prompted

2. **Download and Install Docker Desktop**
   - Download from: [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
   - Run the installer and follow the wizard
   - Enable WSL 2 during installation if prompted
   - Restart your computer after installation

3. **Verify Installation**
   Open a new PowerShell or Command Prompt and run:
   ```bash
   # Check Docker version
   docker --version
   
   # Check Docker Compose version
   docker compose version
   
   # Verify Docker is running
   docker run hello-world
   ```

4. **Configure Docker Desktop**
   - Launch Docker Desktop from the Start menu
   - Go to Settings > Resources > WSL Integration
   - Enable integration with your default WSL distribution
   - Allocate at least 4GB of memory in Settings > Resources > Advanced
   - Apply & Restart Docker Desktop

### Development Setup

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd PMS
   ```

2. **Set Up Environment Variables**
   ```bash
   # Copy example environment file
   copy .env.example .env
   ```
   - Edit `.env` with your configuration (at minimum, set strong passwords)
   - Ensure `POSTGRES_PASSWORD` matches in both `.env` and `docker-compose.yml`

### Start Development Environment

1. **Start Development Environment**
   ```bash
   # Start all services with hot-reloading
   docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
   ```

2. **Verify Services**
   ```bash
   # Check container status (should show 3 running containers)
   docker compose ps
   
   # View logs (press Ctrl+C to exit)
   docker compose logs -f
   ```

3. **Access the Applications**
   - Frontend Development: http://localhost:3000
     - Hot-reloading enabled
     - Development tools available
   - Backend API: http://localhost:8000
     - RESTful endpoints
     - Database connection
   - API Documentation: http://localhost:8000/docs
     - Interactive Swagger UI
     - Test endpoints directly
   - Database: localhost:5432
     - Username: pms_user
     - Database: pms_db
     - Port: 5432

4. **Monitor Services**
   ```bash
   # View resource usage
   docker stats
   
   # View container logs
   docker compose logs -f backend
   docker compose logs -f frontend
   
   # View database logs
   docker compose logs -f db
   ```

## Using Dockerized Modules

### Backend Module

#### Start Backend Service
```bash
# Start only backend and database services
docker compose up -d db backend

# View backend logs
docker compose logs -f backend
```

#### Run Backend Commands
```bash
# Access backend container shell
docker compose exec backend bash

# Run database migrations
docker compose exec backend alembic upgrade head

# Run tests
docker compose exec backend pytest

# Run linters
docker compose exec backend black .
docker compose exec backend isort .

# Run specific test file
docker compose exec backend pytest tests/test_tasks.py -v
```

#### API Access
- Base URL: `http://localhost:8000`
- Interactive Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/api/health`

### Frontend Module

#### Start Frontend Service
```bash
# Start frontend with hot-reloading
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d frontend

# View frontend logs
docker compose logs -f frontend
```

#### Run Frontend Commands
```bash
# Access frontend container shell
docker compose exec frontend sh

# Install new dependency
docker compose exec frontend npm install <package-name>

# Run tests (if configured)
docker compose exec frontend npm test

# Run linter (if configured)
docker compose exec frontend npm run lint
```

#### Frontend Access
- Development: `http://localhost:3000`
- Production: `http://localhost` (when using production compose)

### Production Deployment

```bash
# Build and start production containers
docker-compose up -d --build
```

4. **Access the services**
   - Frontend: http://localhost:3000 (development) or http://localhost (production)
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Database: localhost:5432
   - (Optional) pgAdmin: http://localhost:5050 (if enabled)

### Development Workflow

#### First-Time Setup

1. **Initialize Database**
   ```bash
   # Run migrations
   docker compose exec backend alembic upgrade head
   
   # Create initial data (if needed)
   # docker compose exec backend python scripts/seed_data.py
   ```

2. **Verify Database Connection**
   ```bash
   # Connect to PostgreSQL
   docker compose exec db psql -U pms_user -d pms_db -c "\dt"
   ```

#### Daily Development

1. **Start Services**
   ```bash
   # Start all services
   docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
   ```

2. **Work on Features**
   - Frontend changes in `frontend/` are automatically reflected
   - Backend changes in `backend/` trigger auto-reload
   - Database persists between restarts

3. **Run Tests**
   ```bash
   # Run all tests
   docker compose exec backend pytest
   
   # Run specific test file
   docker compose exec backend pytest tests/test_tasks.py -v
   
   # Run with coverage
   docker compose exec backend pytest --cov=app
   ```

4. **Stop Services**
   ```bash
   # Stop all services
   docker compose down
   
   # Stop and remove volumes (caution: deletes data)
   # docker compose down -v
   ```

### Troubleshooting

1. **Port Conflicts**
   - Check for other services using ports 3000, 8000, or 5432
   - Change ports in `docker-compose.yml` if needed

2. **Container Issues**
   ```bash
   # Rebuild containers
   docker compose build --no-cache
   
   # View container logs
   docker compose logs [service_name]
   
   # Access container shell
   docker compose exec backend bash
   ```

3. **Database Problems**
   ```bash
   # Reset database (warning: deletes all data)
   docker compose down -v
   docker compose up -d
   docker compose exec backend alembic upgrade head
   ```

### Production Deployment

For production, use:
```bash
# Build and start in production mode
docker compose -f docker-compose.yml up -d --build

# View logs
docker compose logs -f

# Apply migrations
docker compose exec backend alembic upgrade head
```

### Useful Commands

```bash
# List all containers
docker ps -a

# View resource usage
docker system df

# Prune unused resources
docker system prune

# View network configuration
docker network ls
docker network inspect pms_pms-network
```

### Development Workflow

#### Frontend Development
- **Hot-reloading**: Changes in `frontend/src` auto-refresh the browser
- **Environment Variables**: Set in `.env` with `REACT_APP_` prefix
- **API Proxying**: Configured to `http://backend:8000` in development
- **Debugging**: Access React DevTools in browser

#### Backend Development
- **Auto-reload**: Code changes trigger server restart
- **Database**:
  - Persistent volume for development data
  - Reset with `docker compose down -v` (warning: deletes data)
- **Testing**:
  ```bash
  # Run all tests with coverage
  docker compose exec backend pytest --cov=app
  
  # Run specific test with detailed output
  docker compose exec backend pytest -v tests/test_projects.py::test_create_project
  ```

#### Common Tasks

**Reset Development Environment**
```bash
# Stop and remove all containers and volumes
docker compose down -v

# Rebuild and start
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build

# Run migrations
docker compose exec backend alembic upgrade head
```

**View Logs**
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend

docker compose logs -f frontend

# Database logs
docker compose logs -f db
```

**Check Service Status**
```bash
# Running containers
docker compose ps

# Resource usage
docker stats

# Network configuration
docker network inspect pms_pms-network
```

- **Rebuild containers** after dependency changes:
  ```bash
  docker-compose -f docker-compose.yml -f docker-compose.dev.yml build --no-cache
  ```

- **View logs**:
  ```bash
  # All services
  docker-compose logs -f
  
  # Specific service
  docker-compose logs -f backend
  ```

### Development Commands

#### Backend
```bash
# Start a shell in the backend container
docker-compose exec backend bash

# Run tests
docker-compose exec backend pytest

# Run database migrations
docker-compose exec backend alembic upgrade head

# Run linter
docker-compose exec backend black .
docker-compose exec backend isort .

# Run tests with coverage
docker-compose exec backend pytest --cov=app --cov-report=term-missing
```

#### Frontend
```bash
# Access frontend container shell
docker-compose exec frontend sh

# Install new dependencies (from host)
docker-compose exec frontend npm install <package-name>

# Run tests (if configured)
docker-compose exec frontend npm test

# Run linter (if configured)
docker-compose exec frontend npm run lint
```

- **Stop services**:
  ```bash
  docker-compose down
  ```

## Getting Started

### Prerequisites (Non-Docker Setup)

### Prerequisites

#### Backend
- Python 3.10+
- PostgreSQL 16.8 (recommended) or 13+
- Poetry (Python package manager) - Install with:
  ```bash
  pip install poetry
  ```

#### Frontend
- Node.js 18+ (LTS recommended)
- npm (comes with Node.js) or yarn

### Database Setup

1. **Install PostgreSQL**
   - Download and install from [PostgreSQL Official Site](https://www.postgresql.org/download/)
   - During installation, remember the password you set for the `postgres` user
   - Make sure to add PostgreSQL to your system PATH

2. **Create Database**
   ```bash
   # Connect to PostgreSQL
   psql -U postgres
   
   # Create database
   CREATE DATABASE pms_db;
   
   # Create a dedicated user (optional but recommended)
   CREATE USER pms_user WITH PASSWORD 'your_secure_password';
   GRANT ALL PRIVILEGES ON DATABASE pms_db TO pms_user;
   \q
   ```

3. **Configure Environment Variables**
   Create a `.env` file in the `backend` directory:
   ```env
   # Database
   DATABASE_URL=postgresql+asyncpg://pms_user:your_secure_password@localhost:5432/pms_db
   
   # JWT
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   
   # App
   DEBUG=True
   ```

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd PMS
   ```

2. **Set up the backend**
   ```bash
   # Navigate to backend directory
   cd backend
   
   # Install Python dependencies
   poetry install
   
   # Install additional dependencies if needed
   poetry add fastapi uvicorn sqlalchemy asyncpg alembic pydantic python-jose passlib python-dotenv pydantic-settings pydantic[email] psycopg-binary python-multipart bcrypt
   
   # Initialize and set up database
   poetry run python -m alembic upgrade head

   # Verify current migration state
   poetry run python -m alembic current
   
   # Create initial admin user (optional)
   poetry run python create_test_user.py
   
   # Start the development server
   poetry run uvicorn main:app --reload
   ```

### Database Migrations with Alembic

When you make changes to your SQLAlchemy models, you'll need to create and apply migrations:

1. **Create a new migration**
   ```bash
   cd backend
   poetry run alembic revision --autogenerate -m "Your migration message"
   ```

2. **Review the generated migration**
   - Check the generated migration file in `alembic/versions/`
   - Make sure it includes all the expected changes

3. **Apply the migration**
   ```bash
   poetry run alembic upgrade head
   ```

4. **Common Alembic commands**
   ```bash
   # Show current revision
   poetry run alembic current
   
   # Show migration history
   poetry run alembic history
   
   # Revert to a previous version
   poetry run alembic downgrade -1  # Go back one migration
   poetry run alembic downgrade <revision_id>  # Go to specific revision
   ```

## Testing

The application includes a comprehensive test suite using `pytest` with `pytest-asyncio` for async testing. The test suite includes unit tests and integration tests for the API endpoints.

### Current Test Coverage

As of the latest test run, the code coverage is as follows:

- **Overall Coverage**: 61%
- **Key Components**:
  - `application/dtos.py`: 100%
  - `infrastructure/models.py`: 100%
  - `application/use_cases/task_management.py`: 80%
  - `application/use_cases/project_management.py`: 61%
  - `infrastructure/repositories.py`: 47%
  - `api/routes.py`: 36%

### Prerequisites

1. The test suite uses an in-memory SQLite database for testing
2. Install the test dependencies:

```bash
cd backend
poetry add --dev pytest pytest-asyncio pytest-cov pytest-mock httpx
```

### Running Tests

1. **Run all tests**
   ```bash
   cd backend
   poetry run pytest -v
   ```

2. **Run tests with coverage report**
   ```bash
   poetry run pytest --cov=application --cov=infrastructure --cov=api --cov-report=term-missing
   ```

3. **Run a specific test file**
   ```bash
   poetry run pytest tests/test_tasks.py -v
   ```

4. **Run a specific test function**
   ```bash
   poetry run pytest tests/test_tasks.py::test_update_task -v
   ```

### Test Structure

- `tests/` - Contains all test files
  - `conftest.py` - Test fixtures and configuration
  - `test_auth.py` - Authentication endpoint tests
  - `test_projects.py` - Project management endpoint tests
  - `test_tasks.py` - Task management endpoint tests
- `tests/unit/` - Unit tests for individual components
  - `test_task_management.py` - Task management use case tests

### Test Database

- Uses SQLite in-memory database for fast test execution
- Database schema is created fresh for each test session
- Test data is automatically set up in fixtures
- Each test runs in a transaction that's rolled back after completion

### Recent Fixes

- Fixed task update functionality to properly handle SQLAlchemy model updates
- Improved test reliability by fixing database session handling in tests
- Added comprehensive error handling in task update operations

### Known Issues

- Some API endpoints have lower test coverage (particularly in protected routes)
- Some deprecation warnings related to datetime.utcnow() need to be addressed
- Pydantic v2 deprecation warnings should be addressed in a future update

### Writing Tests

1. **Test Fixtures**
   - `client`: Unauthenticated test client
   - `auth_client`: Authenticated test client
   - `test_user`: Test user fixture
   - `test_project`: Test project fixture
   - `test_task`: Test task fixture
   - `db_session`: Database session with test data

2. **Example Test**
   ```python
   async def test_create_project(auth_client, test_user):
       project_data = {
           "name": "New Project",
           "description": "Test project"
       }
       response = auth_client.post("/api/projects/", json=project_data)
       assert response.status_code == 201
       data = response.json()
       assert data["name"] == project_data["name"]
   ```

### SQLAlchemy Configuration

The project uses SQLAlchemy 2.0 with async support. Key configuration files:

1. **Database Engine and Session** (`backend/infrastructure/database.py`)
   ```python
   from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
   from sqlalchemy.orm import sessionmaker
   from core.config import settings
   
   engine = create_async_engine(settings.DATABASE_URL, echo=True)
   AsyncSessionLocal = sessionmaker(
       bind=engine,
       class_=AsyncSession,
       expire_on_commit=False
   )
   
   async def get_db() -> AsyncSession:
       async with AsyncSessionLocal() as session:
           try:
               yield session
               await session.commit()
           except Exception:
               await session.rollback()
               raise
   ```

2. **Using Sessions in Routes**
   ```python
   from fastapi import Depends
   from sqlalchemy.ext.asyncio import AsyncSession
   from infrastructure.database import get_db
   
   @router.get("/items/")
   async def read_items(db: AsyncSession = Depends(get_db)):
       result = await db.execute(select(Item))
       return result.scalars().all()
   ```

3. **Set up the frontend**
   ```bash
   # Open a new terminal and navigate to frontend directory
   cd frontend
   
   # Install dependencies
   npm install
   
   # Start the development server
   npm start
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - API Docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Architecture

### Multi-tenancy & Data Isolation

The application implements a **schema-based multi-tenancy** approach to ensure complete data isolation between different organizations. This approach provides strong security boundaries between tenants while maintaining good performance.

#### Implementation Details

1. **Tenant Identification**
   - Each organization is assigned a unique tenant ID
   - The tenant ID is included in the JWT token upon authentication
   - Middleware extracts and validates the tenant ID for each request

2. **Database Architecture**
   - **Schema-per-tenant**: Each tenant has its own database schema
   - **Shared Database**: All schemas exist within a single PostgreSQL database
   - **Public Schema**: Contains shared lookup tables and migrations

3. **Schema Management**
   ```python
   # Database initialization with schema support
   from sqlalchemy import create_engine, event
   from sqlalchemy.orm import sessionmaker
   
   # Create async engine with schema support
   engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
   
   # Schema switching middleware
   @asynccontextmanager
   async def get_tenant_session(tenant_id: str):
       async with AsyncSession(engine) as session:
           await session.execute(text(f'SET search_path TO {tenant_id}, public'))
           try:
               yield session
               await session.commit()
           except Exception:
               await session.rollback()
               raise
   ```

4. **Request Lifecycle**
   - **Authentication**: User provides credentials and tenant context
   - **Token Generation**: JWT includes tenant ID in the payload
   - **Request Processing**:
     1. Middleware validates JWT and extracts tenant ID
     2. Database connection is configured with the tenant's schema
     3. All subsequent queries are automatically scoped to the tenant's schema
     4. Response is returned with appropriate CORS and security headers

5. **Security Measures**
   - **Database-Level Security**:
     - Row-level security (RLS) policies
     - Schema permissions
     - Connection pooling per tenant
   - **Application-Level Security**:
     - JWT validation and verification
     - Tenant context validation in middleware
     - Input validation using Pydantic models
   - **Prevention Measures**:
     - No direct SQL string interpolation
     - Parameterized queries only
     - Tenant context verification in all data access layers

6. **Performance Considerations**
   - Connection pooling is scoped per tenant
   - Caching strategies respect tenant boundaries
   - Indexes are optimized for tenant-specific queries
   - Database maintenance operations are designed to work with multiple schemas

7. **Migration Strategy**
   - Alembic migrations support multi-tenant schema updates
   - Migrations can be applied to all tenants or specific ones
   - Schema versioning is tracked per tenant

8. **Testing Multi-tenancy**
   - Unit tests verify tenant isolation
   - Integration tests validate cross-tenant access prevention
   - Performance tests ensure scalability with multiple tenants

### Backend Architecture

```
backend/
├── alembic/           # Database migrations
├── api/               # API routes and endpoints
│   ├── dependencies.py # Authentication and dependency injection
│   └── routes/        # Route definitions by feature
├── application/       # Business logic layer
│   ├── use_cases/     # Business use cases
│   └── dtos.py        # Data transfer objects
├── core/              # Core configurations and utilities
│   └── config.py      # Application configuration
├── domain/            # Domain models and entities
├── infrastructure/    # Database models and repositories
│   ├── models.py      # SQLAlchemy models
│   └── repositories/  # Database repositories
└── main.py           # Application entry point
```

### Frontend Architecture

```
frontend/
├── public/            # Static files
└── src/
    ├── api/           # API client and services
    ├── components/    # Reusable UI components
    ├── pages/         # Page components
    ├── App.js         # Main application component
    └── index.js       # Application entry point
```

## API Documentation

### Authentication

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}
```

Response:
```json
{
  "access_token": "jwt.token.here",
  "token_type": "bearer"
}
```

### Projects

#### List Projects
```http
GET /api/projects/
Authorization: Bearer <token>
```

#### Create Project
```http
POST /api/projects/
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "New Project",
  "description": "Project description"
}
```

### Tasks

#### List Tasks
```http
GET /api/tasks/?project_id=<project_id>
Authorization: Bearer <token>
```

#### Create Task
```http
POST /api/tasks/
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "New Task",
  "description": "Task description",
  "project_id": "<project_id>",
  "status": "todo"
}
```

## 🧪 Running Tests

### Backend Tests
```bash
cd backend
poetry run pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🔄 Deployment

### Backend Deployment
1. Set up a production database
2. Update production environment variables
3. Use a production ASGI server:
   ```bash
   pip install gunicorn uvloop httptools
   gunicorn -k uvicorn.workers.UvicornWorker main:app --workers 4
   ```

### Frontend Deployment
1. Create a production build:
   ```bash
   cd frontend
   npm run build
   ```
2. Serve the `build` directory using a static file server or CDN

## 📝 Assumptions

1. **Multi-tenancy**: The system is designed with multi-tenancy in mind, where each organization has isolated data.
2. **Authentication**: JWT-based authentication is used for securing API endpoints.
3. **Frontend-Backend Communication**: The frontend makes API calls to the backend using Axios.
4. **Development Workflow**: Developers will use the development server during development.
5. **Database**: PostgreSQL is used as the primary database with async support.

## 📄 License

[Your License Here]

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://reactjs.org/)
- [Material-UI](https://mui.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)

## Project Structure

```
PMS/
├── backend/         # FastAPI backend service
├── frontend/        # React frontend application
└── README.md        # This file
```

## Documentation

- [Backend Documentation](./backend/README.md)
- [Frontend Documentation](./frontend/README.md)
- [API Documentation](http://localhost:8000/docs) (after starting the backend)

## Development

### Backend Development

```bash
cd backend
poetry install  # Install dependencies
poetry run black .  # Format code
poetry run mypy .  # Type checking
poetry run pytest  # Run tests
```

### Frontend Development

```bash
cd frontend
npm install    # Install dependencies
npm start     # Start development server
npm test      # Run tests
npm run build # Create production build
```

## Deployment

### Backend

1. Configure production environment variables
2. Set up a production database
3. Use a production ASGI server like Uvicorn with Gunicorn

### Frontend

1. Build the production bundle:
   ```bash
   cd frontend
   npm run build
   ```
2. Serve the `build` directory using a static file server or CDN

## License

[Your License Here]
