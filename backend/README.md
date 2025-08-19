# Project Management System - Backend

This is the backend service for the Project Management System, built with FastAPI and PostgreSQL.

## Prerequisites

- Python 3.10 or higher
- PostgreSQL 13 or higher
- Poetry (Python package manager)
- Git

## Testing

### Test Dependencies
Make sure you have the testing dependencies installed:
```bash
poetry add pytest pytest-asyncio pytest-cov httpx pytest-mock --group test
```

### Running Tests

#### Run All Tests
```bash
pytest -v
```

#### Run Tests with Coverage Report
```bash
pytest --cov=application --cov-report=term-missing
```

#### Run Specific Test Module
```bash
# Example: Run all authentication tests
pytest tests/test_auth.py -v

# Example: Run all project tests
pytest tests/test_projects.py -v
```

#### Run Specific Test Function
```bash
# Example: Run a specific test function
pytest tests/test_projects.py::test_create_project -v
```

### Current Test Coverage

```
Name                                               Stmts   Miss  Cover
----------------------------------------------------------------------
application/__init__.py                                0      0   100%
application/dtos.py                                   62      3    95%
application/services.py                               22      6    73%
application/use_cases/__init__.py                      0      0   100%
application/use_cases/project_management.py           92     58    37%
application/use_cases/project_user_management.py      13      6    54%
application/use_cases/task_management.py              69     69     0%
application/use_cases/user_management.py              69     47    32%
----------------------------------------------------------------------
TOTAL                                                327    189    42%
```

### Test Database
Tests use an in-memory SQLite database by default, so no additional setup is needed for running tests.

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd PMS/backend
   ```

2. **Install dependencies**
   ```bash
   # note: if poetry is not installed, run `pip install poetry`, if the problem presists and the term 'poetry' is not recognized,add python -m before poetry
   poetry install

   poetry add fastapi uvicorn sqlalchemy asyncpg alembic pydantic python-jose passlib python-dotenv pydantic-settings pydantic[email] psycopg-binary python-multipart bcrypt
   ```

3. **Set up environment variables**
   Create a `.env` file in the `backend` directory with the following variables:
   ```env
   # Database
   DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/pms_db
   
   # JWT
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

4. **Set up the database**

   a. **Create the PostgreSQL database**
   - Open a command prompt and connect to PostgreSQL or use SQL Shell or pgAdmin to create the database:
     ```bash
     psql -U postgres -c "CREATE DATABASE pms;"
     ```
   - In the PostgreSQL prompt, connect to the db:
     ```sql
     \c pms;
     ```
     or by filling in the details in pgAdmin

   b. **Install required database tools**
   ```bash
   pip install alembic psycopg-binary
   ```

   c. **Run database migrations**
   ```bash
   # From the backend directory
   python -m alembic upgrade head
   ```

   d. **Create a test user (optional)**
   ```bash
   python create_test_user.py
   ```
   This will create a test user with the following credentials:
   - Email: test@example.com
   - Password: testpass123
   - Tenant: test-tenant

## Running the Application

1. **Start the development server**
   ```bash
   python -m uvicorn main:app --reload
   ```
   The API will be available at `http://localhost:8000`

2. **API Documentation**
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
backend/
├── alembic/           # Database migrations
├── api/               # API routes and endpoints
├── application/       # Business logic and use cases
├── core/              # Core configurations and utilities
├── infrastructure/    # Database models and repositories
├── tests/             # Test files
├── .env.example       # Example environment variables
├── alembic.ini        # Alembic configuration
├── main.py            # Application entry point
└── pyproject.toml     # Dependencies and project metadata
```

## Testing

To run tests:

```bash
python -m pytest
```

## Development

- Format code with Black:
  ```bash
  black .
  ```

- Check for type errors:
  ```bash
  mypy .
  ```

## Deployment

For production deployment, consider using:
- Gunicorn with Uvicorn workers
- Environment variables for configuration
- PostgreSQL connection pooling
- Proper SSL/TLS termination

## License

[Your License Here]
