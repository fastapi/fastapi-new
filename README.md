# FastAPI-New

**A modular project generator for FastAPI applications.**

FastAPI-New provides a command-line tool to generate well-structured FastAPI projects with modular architecture, automatic route registration, and clean separation of concerns.

---

<a href="https://github.com/fastapi/fastapi-new/actions?query=workflow%3ATest+event%3Apush+branch%3Amain" target="_blank">
    <img src="https://github.com/fastapi/fastapi-new/actions/workflows/test.yml/badge.svg?event=push&branch=main" alt="Test">
</a>
<a href="https://coverage-badge.samuelcolvin.workers.dev/redirect/fastapi/fastapi-new" target="_blank">
    <img src="https://coverage-badge.samuelcolvin.workers.dev/fastapi/fastapi-new.svg" alt="Coverage">
</a>
<a href="https://pypi.org/project/fastapi-new" target="_blank">
    <img src="https://img.shields.io/pypi/v/fastapi-new?color=%2334D058&label=pypi%20package" alt="Package version">
</a>
<a href="https://pypi.org/project/fastapi-new" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/fastapi-new.svg?color=%2334D058" alt="Supported Python versions">
</a>

---

## Overview

FastAPI-New is a project scaffolding tool that generates production-ready FastAPI projects with:

- **Modular Architecture** - Organize your application into independent, reusable modules
- **Automatic Registration** - Modules are automatically discovered and loaded
- **MSSR Pattern** - Structured layers for Models, Schemas, Services, and Repositories
- **CLI Tools** - Generate modules and manage database configurations from the command line
- **Database Flexibility** - Works with any database or ORM of your choice
- **Minimal Boilerplate** - Clean starter templates with helpful examples

## Installation

FastAPI-New requires [uv](https://docs.astral.sh/uv/) for project management.

### Install uv

```bash
# macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Create a Project

```bash
uvx fastapi-new myproject
```

This creates a new FastAPI project in the `myproject` directory.

## Quick Example

```bash
# Create a new project
uvx fastapi-new myapi
cd myapi

# Generate application modules
fastapi-new createapp users
fastapi-new createapp products

# Start the development server
uv run fastapi dev
```

Visit [http://localhost:8000/docs](http://localhost:8000/docs) to see your API documentation.

## Project Structure

A newly created project has the following structure:

```
myproject/
├── app/
│   ├── main.py          # Application entry point
│   ├── core/            # Core application components
│   │   ├── config.py    # Configuration management
│   │   ├── registry.py  # Module registry
│   │   ├── database.py  # Database configuration
│   │   └── security.py  # Security utilities
│   ├── apps/            # Application modules
│   └── db/              # Database layer
│       ├── base.py      # Base model definitions
│       └── session.py   # Session management
├── .env                 # Environment variables
└── pyproject.toml       # Project dependencies
```

### Core Components

#### `main.py`

The application entry point that creates the FastAPI instance and registers all modules:

```python
from fastapi import FastAPI
from app.core.config import settings
from app.core.registry import INSTALLED_APPS

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
)

# Modules are automatically loaded from INSTALLED_APPS
```

#### `core/registry.py`

Manages module registration:

```python
INSTALLED_APPS: list[str] = [
    "users",
    "products",
]
```

#### `core/config.py`

Application settings using Pydantic:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "MyAPI"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
```

## CLI Commands

### Create a New Project

```bash
# Create in a new directory
uvx fastapi-new myproject

# Initialize in current directory
uvx fastapi-new
```

**Options:**
- `--python, -p` - Specify Python version (e.g., `--python 3.12`)

### Generate Application Modules

```bash
fastapi-new createapp <module_name>
```

Creates a new module with the MSSR structure:

```
app/apps/<module_name>/
├── __init__.py
├── models.py        # Data models
├── schemas.py       # Pydantic schemas
├── services.py      # Business logic
├── repositories.py  # Data access layer
├── routes.py        # API routes
└── dependencies.py  # FastAPI dependencies
```

The module is automatically added to `INSTALLED_APPS` in `core/registry.py`.

**Example:**

```bash
fastapi-new createapp users
```

Generates:

```python
# app/apps/users/routes.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_users():
    return {"users": []}
```

### Add Database Support

```bash
fastapi-new add-db <engine>
```

Configures database support for the specified engine.

**Supported engines:**
- `postgres` - PostgreSQL
- `mysql` - MySQL
- `sqlite` - SQLite
- `mongodb` - MongoDB

**Options:**
- `--install, -i` - Automatically install required dependencies

**Example:**

```bash
fastapi-new add-db postgres --install
```

### List Installed Modules

```bash
fastapi-new list
```

Displays all registered application modules.

**Options:**
- `--verbose, -v` - Show detailed module information

### Diagnose Project

```bash
fastapi-new doctor
```

Checks project structure and configuration:
- Required directories exist
- Core files are present
- Module files are valid
- Environment is configured

## Architecture

### MSSR Pattern

FastAPI-New follows the Model-Schema-Service-Repository pattern for clean architecture:

```
Client Request
    ↓
API Route (routes.py)
    ↓
Business Logic (services.py)
    ↓
Data Access (repositories.py)
    ↓
Data Model (models.py)
    ↓
Database
```

**Benefits:**

- **Separation of Concerns** - Each layer has a single responsibility
- **Testability** - Layers can be tested independently
- **Maintainability** - Changes are localized to specific layers
- **Flexibility** - Database or business logic can be swapped easily

### Layer Responsibilities

| Layer | File | Purpose |
|-------|------|---------|
| **Model** | `models.py` | Database schema and ORM models |
| **Schema** | `schemas.py` | Request/response validation with Pydantic |
| **Service** | `services.py` | Business logic and operations |
| **Repository** | `repositories.py` | Database queries and data access |
| **Route** | `routes.py` | HTTP endpoints and request handling |

### Example Implementation

#### Models

```python
# app/apps/users/models.py
from sqlalchemy import Column, Integer, String
from app.db.base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
```

#### Schemas

```python
# app/apps/users/schemas.py
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    name: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    
    class Config:
        from_attributes = True
```

#### Repositories

```python
# app/apps/users/repositories.py
from sqlalchemy.orm import Session
from app.apps.users.models import User

class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_email(self, email: str):
        return self.db.query(User).filter(User.email == email).first()
    
    def create(self, user_data: dict):
        user = User(**user_data)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
```

#### Services

```python
# app/apps/users/services.py
from app.apps.users.repositories import UserRepository
from app.apps.users.schemas import UserCreate

class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository
    
    def create_user(self, user_data: UserCreate):
        # Business logic here
        if self.repository.get_by_email(user_data.email):
            raise ValueError("Email already registered")
        return self.repository.create(user_data.dict())
```

#### Routes

```python
# app/apps/users/routes.py
from fastapi import APIRouter, Depends
from app.apps.users.schemas import UserCreate, UserResponse
from app.apps.users.dependencies import get_user_service

router = APIRouter()

@router.post("/", response_model=UserResponse)
async def create_user(
    user: UserCreate,
    service = Depends(get_user_service)
):
    return service.create_user(user)
```

## Module Registration

Modules are automatically registered when created with `fastapi-new createapp`.

### Manual Registration

To manually register a module, add it to `INSTALLED_APPS` in `app/core/registry.py`:

```python
INSTALLED_APPS: list[str] = [
    "users",
    "products",
    "orders",  # Add your module here
]
```

### How It Works

The `main.py` file automatically loads routes from registered modules:

```python
from importlib import import_module
from app.core.registry import INSTALLED_APPS

for app_name in INSTALLED_APPS:
    try:
        routes = import_module(f"app.apps.{app_name}.routes")
        if hasattr(routes, "router"):
            app.include_router(
                routes.router,
                prefix=f"/api/v1/{app_name}",
                tags=[app_name.capitalize()],
            )
    except ImportError as e:
        print(f"Could not load {app_name}: {e}")
```

## Configuration

### Environment Variables

Configure your application through environment variables in `.env`:

```env
# Application
PROJECT_NAME=MyAPI
PROJECT_DESCRIPTION=My FastAPI Application
VERSION=0.1.0
DEBUG=true

# Database (add when needed)
# DATABASE_URL=postgresql://user:password@localhost/dbname

# Security (add when needed)
# SECRET_KEY=your-secret-key-here
```

### Settings Management

Settings are managed through Pydantic Settings:

```python
# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "MyAPI"
    PROJECT_DESCRIPTION: str = "API Description"
    VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

Access settings anywhere in your application:

```python
from app.core.config import settings

print(settings.PROJECT_NAME)
```

## Database Configuration

FastAPI-New is database-agnostic. Use any database or ORM:

### SQLAlchemy Example

```python
# app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Tortoise ORM Example

```python
# app/core/database.py
from tortoise import Tortoise

async def init_db():
    await Tortoise.init(
        db_url="sqlite://db.sqlite3",
        modules={"models": ["app.apps.users.models"]}
    )
```

### MongoDB Example

```python
# app/core/database.py
from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.mydatabase
```

## Development Workflow

### 1. Create Project

```bash
uvx fastapi-new myapi
cd myapi
```

### 2. Generate Modules

```bash
fastapi-new createapp users
fastapi-new createapp products
fastapi-new createapp orders
```

### 3. Implement Features

Edit the generated files to implement your business logic.

### 4. Check Project Health

```bash
fastapi-new doctor
```

### 5. Run Development Server

```bash
uv run fastapi dev
```

The server will reload automatically when you make changes.

### 6. View API Documentation

Visit [http://localhost:8000/docs](http://localhost:8000/docs) for interactive API documentation.

## Best Practices

### Module Organization

- Keep modules focused on a single domain concept
- Use descriptive module names (e.g., `users`, `orders`, `notifications`)
- Avoid circular dependencies between modules

### Code Structure

- **Models** - Define database schema only
- **Schemas** - Validate and serialize data
- **Repositories** - Isolate database queries
- **Services** - Contain business logic
- **Routes** - Handle HTTP concerns only

### Configuration

- Use environment variables for configuration
- Never commit `.env` files to version control
- Provide `.env.example` as a template

### Testing

```python
# tests/test_users.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_user():
    response = client.post("/api/v1/users/", json={
        "email": "test@example.com",
        "name": "Test User"
    })
    assert response.status_code == 200
```

## Production Deployment

### Using Docker

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install uv && uv pip install -r pyproject.toml

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Using Uvicorn

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Requirements

- **Python** 3.10 or higher
- **uv** for dependency management

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

**Documentation:** [FastAPI Documentation](https://fastapi.tiangolo.com/)  
**Source Code:** [github.com/fastapi/fastapi-new](https://github.com/fastapi/fastapi-new)