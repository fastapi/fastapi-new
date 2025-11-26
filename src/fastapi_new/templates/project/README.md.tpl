# {{project_name}}

A modular enterprise-ready FastAPI application built with [FastAPI-New](https://github.com/fastapi/fastapi-new).

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (recommended package manager)

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd {{project_name}}

# Install dependencies
uv sync

# Copy environment file
cp .env.example .env

# Start development server
uv run fastapi dev
```

Visit [http://localhost:8000](http://localhost:8000) to see your application.

## 📚 Documentation

- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI)
- **Alternative Docs**: [http://localhost:8000/redoc](http://localhost:8000/redoc) (ReDoc)
- **OpenAPI Schema**: [http://localhost:8000/api/v1/openapi.json](http://localhost:8000/api/v1/openapi.json)

## 📁 Project Structure

```
{{project_name}}/
├── app/
│   ├── main.py              # Application entry point
│   ├── __init__.py
│   ├── core/                # Core configuration
│   │   ├── config.py        # Settings management
│   │   ├── registry.py      # App registration system
│   │   ├── database.py      # Database connections
│   │   ├── security.py      # Auth & authorization
│   │   └── container.py     # Dependency injection
│   ├── apps/                # Application modules (MSSR)
│   │   └── <your_apps>/
│   ├── db/                  # Database layer
│   │   ├── base.py          # SQLAlchemy base model
│   │   ├── session.py       # Session management
│   │   └── engines/         # DB engine configurations
│   ├── plugins/             # Plugin modules
│   ├── shared/              # Shared utilities
│   │   ├── exceptions.py    # Custom exceptions
│   │   ├── utils.py         # Utility functions
│   │   └── constants.py     # Application constants
│   └── tests/               # Test suite
├── .env.example             # Environment template
├── .env                     # Environment variables (git ignored)
├── pyproject.toml           # Project dependencies
└── README.md                # This file
```

## 🏗️ Architecture

This project follows the **MSSR Pattern** (Model, Schema, Service, Repository):

```
Client → Route → Service → Repository → Model → Database
```

| Layer | Responsibility |
|-------|----------------|
| **Model** | ORM database models (SQLAlchemy) |
| **Schema** | Pydantic request/response validation |
| **Service** | Business logic |
| **Repository** | Data access abstraction |
| **Route** | API interface (FastAPI endpoints) |

## 🛠️ CLI Commands

### Create a New App Module

```bash
fastapi-new createapp users
```

This generates a complete MSSR module:

```
app/apps/users/
├── __init__.py
├── models.py        # SQLAlchemy models
├── schemas.py       # Pydantic schemas
├── services.py      # Business logic
├── repositories.py  # Data access layer
├── routes.py        # API endpoints
└── dependencies.py  # FastAPI dependencies
```

### Add Database Engine

```bash
# PostgreSQL
fastapi-new add-db postgres

# MySQL
fastapi-new add-db mysql

# SQLite (default)
fastapi-new add-db sqlite

# MongoDB
fastapi-new add-db mongodb
```

### List Installed Apps

```bash
fastapi-new list
```

### Diagnose Project

```bash
fastapi-new doctor
```

## ⚙️ Configuration

Configuration is managed through environment variables. See `.env.example` for all available options.

### Key Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Environment mode (dev/staging/prod) | `dev` |
| `DEBUG` | Enable debug mode | `true` |
| `DATABASE_URL` | Database connection string | `sqlite:///./app.db` |
| `SECRET_KEY` | JWT signing key | (change in production!) |
| `API_V1_PREFIX` | API version prefix | `/api/v1` |

## 🗄️ Database

### Migrations (with Alembic)

```bash
# Initialize Alembic (first time only)
uv run alembic init alembic

# Create a migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback
uv run alembic downgrade -1
```

### Supported Databases

- **PostgreSQL** (recommended for production)
- **MySQL** / **MariaDB**
- **SQLite** (default, great for development)
- **MongoDB** (NoSQL support)

## 🔐 Security

### Authentication

JWT-based authentication is built-in:

```python
from app.core.security import get_current_user_token, RoleChecker

# Require authentication
@router.get("/protected")
async def protected_route(token_data: TokenData = Depends(get_current_user_token)):
    return {"user_id": token_data.user_id}

# Require specific role
@router.get("/admin", dependencies=[Depends(RoleChecker(["admin"]))])
async def admin_only():
    return {"message": "Welcome admin"}
```

### Rate Limiting

Built-in rate limiting support:

```python
from app.core.security import RateLimiter

rate_limiter = RateLimiter(requests=100, window=60)

@router.get("/api/resource", dependencies=[Depends(rate_limiter)])
async def rate_limited_endpoint():
    return {"data": "resource"}
```

## 🧪 Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Run specific test file
uv run pytest tests/test_main.py

# Run with verbose output
uv run pytest -v
```

## 🚢 Deployment

### Production Checklist

- [ ] Set `ENVIRONMENT=prod`
- [ ] Set `DEBUG=false`
- [ ] Generate a strong `SECRET_KEY`
- [ ] Configure production database
- [ ] Set up proper CORS origins
- [ ] Enable HTTPS
- [ ] Configure logging
- [ ] Set up monitoring (Sentry, etc.)

### Docker

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy project files
COPY . .

# Install dependencies
RUN uv sync --frozen

# Run the application
CMD ["uv", "run", "fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/{{project_name}}
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB={{project_name}}
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## 📖 Learn More

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org)
- [Pydantic Documentation](https://docs.pydantic.dev)
- [uv Documentation](https://docs.astral.sh/uv)

## 📝 License

This project is licensed under the MIT License.

---

Built with ❤️ using [FastAPI-New](https://github.com/fastapi/fastapi-new)
