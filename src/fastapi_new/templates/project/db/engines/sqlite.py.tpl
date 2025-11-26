"""
SQLite Database Engine Configuration
Provides SQLite-specific database setup and utilities.

SQLite is the default database for development and testing.
For production, consider PostgreSQL or MySQL.
"""

import os
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings


def get_sqlite_url(async_mode: bool = False) -> str:
    """
    Get SQLite connection URL.

    Args:
        async_mode: If True, returns aiosqlite URL; otherwise returns standard URL

    Returns:
        SQLite connection string
    """
    url = settings.DATABASE_URL

    if async_mode:
        # Convert to async driver (aiosqlite)
        if url.startswith("sqlite:///"):
            return url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)

    return url


def get_database_path() -> Path | None:
    """
    Extract the database file path from the connection URL.

    Returns:
        Path object or None for in-memory database
    """
    url = settings.DATABASE_URL
    if url.startswith("sqlite:///"):
        path_str = url.replace("sqlite:///", "")
        if path_str and path_str != ":memory:":
            return Path(path_str)
    return None


def ensure_database_directory() -> None:
    """Create the database directory if it doesn't exist."""
    db_path = get_database_path()
    if db_path:
        db_path.parent.mkdir(parents=True, exist_ok=True)


def get_engine_options() -> dict[str, Any]:
    """
    Get SQLite engine options.

    Returns:
        Dictionary of engine configuration options
    """
    url = settings.DATABASE_URL
    is_memory = ":memory:" in url or url == "sqlite://"

    options: dict[str, Any] = {
        "echo": settings.DATABASE_ECHO,
        "connect_args": {"check_same_thread": False},
    }

    # Use StaticPool for in-memory databases to maintain single connection
    if is_memory:
        options["poolclass"] = StaticPool

    return options


def get_async_engine_options() -> dict[str, Any]:
    """
    Get SQLite async engine options.

    Returns:
        Dictionary of async engine configuration options
    """
    return {
        "echo": settings.DATABASE_ECHO,
    }


# Ensure database directory exists
ensure_database_directory()

# Create sync engine
engine = create_engine(
    get_sqlite_url(async_mode=False),
    **get_engine_options(),
)

# Create sync session factory
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

# Create async engine
async_engine = create_async_engine(
    get_sqlite_url(async_mode=True),
    **get_async_engine_options(),
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


# Enable foreign key constraints for SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection: Any, connection_record: Any) -> None:
    """Enable foreign key support and other pragmas for SQLite."""
    cursor = dbapi_connection.cursor()
    # Enable foreign key constraints
    cursor.execute("PRAGMA foreign_keys=ON")
    # Enable WAL mode for better concurrency (only for file-based databases)
    cursor.execute("PRAGMA journal_mode=WAL")
    # Synchronous mode for better performance (NORMAL is good balance)
    cursor.execute("PRAGMA synchronous=NORMAL")
    # Increase cache size (negative value = KB, positive = pages)
    cursor.execute("PRAGMA cache_size=-64000")  # 64MB cache
    # Store temp tables in memory
    cursor.execute("PRAGMA temp_store=MEMORY")
    cursor.close()


def get_db() -> Session:
    """
    Sync database session dependency.

    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncSession:
    """
    Async database session dependency.

    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_async_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# SQLite-specific utilities
async def check_connection() -> bool:
    """
    Check if SQLite connection is healthy.

    Returns:
        True if connection is successful, False otherwise
    """
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


async def get_database_version() -> str | None:
    """
    Get SQLite version.

    Returns:
        Version string or None if connection fails
    """
    try:
        async with async_engine.connect() as conn:
            result = await conn.execute(text("SELECT sqlite_version()"))
            row = result.fetchone()
            return row[0] if row else None
    except Exception:
        return None


def get_database_size() -> str | None:
    """
    Get the size of the database file.

    Returns:
        Human-readable database size or None if not available
    """
    db_path = get_database_path()
    if db_path and db_path.exists():
        size_bytes = db_path.stat().st_size
        # Convert to human-readable format
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} TB"
    return None


async def table_exists(table_name: str) -> bool:
    """
    Check if a table exists in the database.

    Args:
        table_name: Name of the table

    Returns:
        True if table exists, False otherwise
    """
    try:
        async with async_engine.connect() as conn:
            result = await conn.execute(
                text(
                    "SELECT name FROM sqlite_master "
                    "WHERE type='table' AND name = :table"
                ),
                {"table": table_name},
            )
            return result.fetchone() is not None
    except Exception:
        return False


async def get_all_tables() -> list[str]:
    """
    Get list of all tables in the database.

    Returns:
        List of table names
    """
    try:
        async with async_engine.connect() as conn:
            result = await conn.execute(
                text(
                    "SELECT name FROM sqlite_master "
                    "WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                )
            )
            return [row[0] for row in result.fetchall()]
    except Exception:
        return []


async def get_table_row_count(table_name: str) -> int | None:
    """
    Get the row count for a table.

    Args:
        table_name: Name of the table

    Returns:
        Row count or None if query fails
    """
    try:
        async with async_engine.connect() as conn:
            # Note: Using parameterized query for table name isn't directly supported
            # This is safe since table_exists is checked first
            if await table_exists(table_name):
                result = await conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                row = result.fetchone()
                return row[0] if row else None
    except Exception:
        pass
    return None


async def get_table_info(table_name: str) -> list[dict[str, Any]]:
    """
    Get column information for a table.

    Args:
        table_name: Name of the table

    Returns:
        List of column information dictionaries
    """
    try:
        async with async_engine.connect() as conn:
            result = await conn.execute(text(f"PRAGMA table_info({table_name})"))
            columns = []
            for row in result.fetchall():
                columns.append({
                    "cid": row[0],
                    "name": row[1],
                    "type": row[2],
                    "notnull": bool(row[3]),
                    "default_value": row[4],
                    "pk": bool(row[5]),
                })
            return columns
    except Exception:
        return []


async def vacuum_database() -> bool:
    """
    Run VACUUM to optimize the database file.
    This reclaims unused space and defragments the database.

    Returns:
        True if successful, False otherwise
    """
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("VACUUM"))
        return True
    except Exception:
        return False


async def analyze_database() -> bool:
    """
    Run ANALYZE to update database statistics.
    This helps the query optimizer make better decisions.

    Returns:
        True if successful, False otherwise
    """
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("ANALYZE"))
        return True
    except Exception:
        return False


def backup_database(backup_path: str | Path) -> bool:
    """
    Create a backup of the database file.

    Args:
        backup_path: Path to save the backup

    Returns:
        True if successful, False otherwise
    """
    import shutil

    db_path = get_database_path()
    if db_path and db_path.exists():
        try:
            shutil.copy2(db_path, backup_path)
            return True
        except Exception:
            pass
    return False


async def get_pragma_value(pragma_name: str) -> Any:
    """
    Get the value of a SQLite PRAGMA.

    Args:
        pragma_name: Name of the PRAGMA

    Returns:
        PRAGMA value or None
    """
    try:
        async with async_engine.connect() as conn:
            result = await conn.execute(text(f"PRAGMA {pragma_name}"))
            row = result.fetchone()
            return row[0] if row else None
    except Exception:
        return None


async def get_database_stats() -> dict[str, Any]:
    """
    Get various database statistics.

    Returns:
        Dictionary with database statistics
    """
    stats: dict[str, Any] = {
        "version": await get_database_version(),
        "file_size": get_database_size(),
        "tables": await get_all_tables(),
        "journal_mode": await get_pragma_value("journal_mode"),
        "cache_size": await get_pragma_value("cache_size"),
        "foreign_keys": await get_pragma_value("foreign_keys"),
    }

    # Get row counts for each table
    table_counts = {}
    for table in stats["tables"]:
        count = await get_table_row_count(table)
        if count is not None:
            table_counts[table] = count
    stats["table_row_counts"] = table_counts

    return stats


def execute_raw_sql(sql: str, params: dict[str, Any] | None = None) -> Any:
    """
    Execute raw SQL query (sync).

    Args:
        sql: SQL query string
        params: Query parameters

    Returns:
        Query result
    """
    with SessionLocal() as session:
        result = session.execute(text(sql), params or {})
        session.commit()
        return result


async def execute_raw_sql_async(sql: str, params: dict[str, Any] | None = None) -> Any:
    """
    Execute raw SQL query (async).

    Args:
        sql: SQL query string
        params: Query parameters

    Returns:
        Query result
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(text(sql), params or {})
        await session.commit()
        return result
