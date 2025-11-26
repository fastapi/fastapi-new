# FastAPI-New

A modular enterprise framework for FastAPI with Django-like structure. ✨

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

## Overview

FastAPI-New is an opinionated CLI-powered framework layer on top of FastAPI that provides:

- 🏗️ **Django-like structure** - Modular app architecture with auto-registration
- 📦 **MSSR Pattern** - Model, Schema, Service, Repository for clean separation of concerns
- 🔧 **CLI-driven development** - Generate apps and configure databases with simple commands
- 🗄️ **Multi-database support** - PostgreSQL, MySQL, SQLite, MongoDB out of the box
- 🔐 **Security built-in** - JWT, OAuth2, RBAC, and rate limiting utilities
- 🧪 **Test-ready** - Pytest configuration with fixtures included

## Quick Start

### Prerequisites

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) following their guide for your system.

### Create a New Project

```bash
uvx fastapi-new myproject
cd myproject
```

### Create an App Module

```bash
fastapi-new createapp users
```

### Start the Development Server

```bash
uv run fastapi dev
```

Open your browser at [http://localhost:8000/docs](http://localhost:8000/docs) to see the API documentation! 🚀

## CLI Commands

| Command | Description |
|---------|-------------|
| `uvx fastapi-new <name>` | Create a new FastAPI-New project |
| `fastapi-new createapp <name>` | Create a new MSSR app module |
| `fastapi-new add-db <engine>` | Add database engine support |
| `fastapi-new list` | List installed app modules |
| `fastapi-new doctor` | Diagnose project structure |

### Create a New Project

```bash
# Create in a new directory
uvx fastapi-new awesomeapp

# Or initialize in current directory
uvx fastapi-new
```

### Create App Modules

```bash
# Create a users app
fastapi-new createapp users

# Create a products app
fastapi-new createapp products
```

This generates the MSSR structure:

```
app/apps/users/
├── __init__.py
├── models.py        # SQLAlchemy ORM models
├── schemas.py       # Pydantic schemas
├── services.py      # Business logic
├── repositories.py  # Data access layer
├── routes.py        # API endpoints
└── dependencies.py  # FastAPI dependencies
```

Apps are automatically registered in `INSTALLED_APPS`.

### Add Database Support

```bash
# Add PostgreSQL
fastapi-new add-db postgres

# Add with auto-install dependencies
fastapi-new add-db postgres --install

# Supported engines: postgres, mysql, sqlite, mongodb
```

### List Installed Apps

```bash
fastapi-new list

# With detailed information
fastapi-new list -v
```

### Diagnose Project

```bash
fastapi-new doctor
```

## Project Structure

```
myproject/
├── app/
│   ├── main.py              # Application entry point
│   ├── core/                # Core configuration
│   │   ├── config.py        # Settings management
│   │   ├── registry.py      # App auto-registration
│   │   ├── database.py      # Database connections
│   │   ├── security.py      # Auth & authorization
│   │   └── container.py     # Dependency injection
│   ├── apps/                # Application modules
│   │   └── users/           # Example app (MSSR pattern)
│   ├── db/                  # Database layer
│   │   ├── base.py          # SQLAlchemy base model
│   │   ├── session.py       # Session management
│   │   └── engines/         # DB-specific configs
│   ├── plugins/             # Plugin modules
│   ├── shared/              # Shared utilities
│   │   ├── exceptions.py    # Custom exceptions
│   │   ├── utils.py         # Utility functions
│   │   └── constants.py     # Constants & enums
│   └── tests/               # Test suite
├── .env                     # Environment variables
├── .env.example             # Environment template
└── pyproject.toml           # Dependencies
```

## Architecture: MSSR Pattern

FastAPI-New follows the **Model-Schema-Service-Repository** pattern:

```
Client → Route → Service → Repository → Model → Database
```

| Layer | Responsibility |
|-------|----------------|
| **Model** | SQLAlchemy ORM database models |
| **Schema** | Pydantic request/response validation |
| **Service** | Business logic |
| **Repository** | Data access abstraction |
| **Route** | API interface |

This ensures:
- ✅ Clean separation of concerns
- ✅ Easy testing & mocking
- ✅ Replaceable database layers
- ✅ Maintainable codebase

## Auto-Registration System

Apps are automatically loaded via `INSTALLED_APPS` in `app/core/registry.py`:

```python
INSTALLED_APPS = [
    "users",
    "products",
]
```

The `main.py` automatically registers routes:

```python
for module in INSTALLED_APPS:
    router = import_module(f"app.apps.{module}.routes").router
    app.include_router(router)
```

## Configuration

Environment variables are managed through `.env`:

```env
# Application
PROJECT_NAME=myproject
ENVIRONMENT=dev
DEBUG=true

# Database
DATABASE_ENGINE=sqlite
DATABASE_URL=sqlite:///./app.db

# Security
SECRET_KEY=your-secret-key
```

## Developer Workflow

```bash
# 1. Create project
uvx fastapi-new myproject
cd myproject

# 2. Create app modules
fastapi-new createapp users
fastapi-new createapp products

# 3. Add database
fastapi-new add-db postgres --install

# 4. Run development server
uv run fastapi dev
```

## Supported Databases

| Engine | Driver | Command |
|--------|--------|---------|
| PostgreSQL | asyncpg, psycopg2 | `fastapi-new add-db postgres` |
| MySQL | aiomysql, pymysql | `fastapi-new add-db mysql` |
| SQLite | aiosqlite | `fastapi-new add-db sqlite` |
| MongoDB | motor, pymongo | `fastapi-new add-db mongodb` |

## Security Features

Built-in security utilities in `app/core/security.py`:

- **JWT Authentication** - Token generation and validation
- **Password Hashing** - bcrypt-based password security
- **Role-Based Access Control** - `RoleChecker` dependency
- **Rate Limiting** - Request rate limiting middleware
- **OAuth2** - OAuth2 password flow support

## License

This project is licensed under the terms of the MIT license.