"""
Database Engines Module
Provides database-specific configurations for different database engines.

Supported Engines:
    - PostgreSQL (postgres.py)
    - MySQL (mysql.py)
    - SQLite (sqlite.py)
    - MongoDB (mongodb.py)

Usage:
    The appropriate engine is loaded based on DATABASE_ENGINE setting in config.

    from app.db.engines import get_db, get_async_db

    @app.get("/items")
    async def get_items(db = Depends(get_async_db)):
        # Works with any configured database
        pass

Engine Selection:
    Set DATABASE_ENGINE in your .env file:
        DATABASE_ENGINE=postgres  # PostgreSQL
        DATABASE_ENGINE=mysql     # MySQL
        DATABASE_ENGINE=sqlite    # SQLite (default)
        DATABASE_ENGINE=mongodb   # MongoDB
"""

from typing import Any

from app.core.config import settings


def get_engine_module() -> Any:
    """
    Dynamically import the appropriate database engine module.

    Returns:
        The database engine module based on DATABASE_ENGINE setting
    """
    engine = settings.DATABASE_ENGINE.lower()

    if engine == "postgres" or engine == "postgresql":
        from app.db.engines import postgres
        return postgres
    elif engine == "mysql":
        from app.db.engines import mysql
        return mysql
    elif engine == "sqlite":
        from app.db.engines import sqlite
        return sqlite
    elif engine == "mongodb" or engine == "mongo":
        from app.db.engines import mongodb
        return mongodb
    else:
        # Default to SQLite
        from app.db.engines import sqlite
        return sqlite


# Dynamic exports based on configured engine
_engine_module = get_engine_module()

# Export common database functions
get_db = _engine_module.get_db
get_async_db = _engine_module.get_async_db
check_connection = _engine_module.check_connection
get_database_version = _engine_module.get_database_version

# Export engine-specific objects if available
if hasattr(_engine_module, "engine"):
    engine = _engine_module.engine

if hasattr(_engine_module, "async_engine"):
    async_engine = _engine_module.async_engine

if hasattr(_engine_module, "SessionLocal"):
    SessionLocal = _engine_module.SessionLocal

if hasattr(_engine_module, "AsyncSessionLocal"):
    AsyncSessionLocal = _engine_module.AsyncSessionLocal


__all__ = [
    "get_db",
    "get_async_db",
    "check_connection",
    "get_database_version",
    "get_engine_module",
]
