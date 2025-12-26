"""
{{project_name}} - FastAPI Application
Generated with FastAPI-New

A modular enterprise-ready FastAPI project following the MSSR pattern
(Model, Schema, Service, Repository).

Project Structure:
    app/
    ├── main.py           # Application entry point
    ├── core/             # Core configuration and utilities
    │   ├── config.py     # Settings management
    │   ├── registry.py   # App registration system
    │   ├── database.py   # Database connections
    │   ├── security.py   # Authentication & authorization
    │   └── container.py  # Dependency injection
    ├── apps/             # Application modules
    ├── db/               # Database models and sessions
    ├── plugins/          # Remote and local plugins
    ├── shared/           # Shared utilities and exceptions
    └── tests/            # Test suite

Quick Start:
    # Start development server
    uv run fastapi dev

    # Create a new app module
    fastapi-new createapp <app_name>

    # Add database engine
    fastapi-new add-db postgres

Documentation:
    - API Docs: http://localhost:8000/docs
    - ReDoc: http://localhost:8000/redoc
"""

__version__ = "0.1.0"
