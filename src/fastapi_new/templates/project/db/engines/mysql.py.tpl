"""
MySQL Database Engine Configuration
Provides MySQL-specific database setup and utilities.
"""

from typing import Any

from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool

from app.core.config import settings


def get_mysql_url(async_mode: bool = False) -> str:
    """
    Get MySQL connection URL.

    Args:
        async_mode: If True, returns aiomysql URL; otherwise returns pymysql URL

    Returns:
        MySQL connection string
    """
    url = settings.DATABASE_URL

    if async_mode:
        # Convert to async driver (aiomysql)
        if url.startswith("mysql://"):
            return url.replace("mysql://", "mysql+aiomysql://", 1)
        elif url.startswith("mysql+pymysql://"):
            return url.replace("mysql+pymysql://", "mysql+aiomysql://", 1)
    else:
        # Ensure sync driver (pymysql)
        if url.startswith("mysql://"):
            return url.replace("mysql://", "mysql+pymysql://", 1)

    return url


def get_engine_options() -> dict[str, Any]:
    """
    Get MySQL engine options optimized for production.

    Returns:
        Dictionary of engine configuration options
    """
    return {
        "echo": settings.DATABASE_ECHO,
        "pool_size": settings.DATABASE_POOL_SIZE,
        "max_overflow": settings.DATABASE_MAX_OVERFLOW,
        "pool_pre_ping": True,  # Enable connection health checks
        "pool_recycle": 3600,  # Recycle connections after 1 hour
        "poolclass": QueuePool,
        "connect_args": {
            "connect_timeout": 10,
            "charset": "utf8mb4",
            "autocommit": False,
        },
    }


def get_async_engine_options() -> dict[str, Any]:
    """
    Get MySQL async engine options.

    Returns:
        Dictionary of async engine configuration options
    """
    return {
        "echo": settings.DATABASE_ECHO,
        "pool_size": settings.DATABASE_POOL_SIZE,
        "max_overflow": settings.DATABASE_MAX_OVERFLOW,
        "pool_pre_ping": True,
        "pool_recycle": 3600,
    }


# Create sync engine
engine = create_engine(
    get_mysql_url(async_mode=False),
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
    get_mysql_url(async_mode=True),
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


# Set SQL mode and charset on connection
@event.listens_for(engine, "connect")
def set_mysql_options(dbapi_connection: Any, connection_record: Any) -> None:
    """Configure MySQL connection options."""
    cursor = dbapi_connection.cursor()
    # Set SQL mode for stricter validation
    cursor.execute("SET sql_mode = 'STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO'")
    # Set timezone to UTC
    cursor.execute("SET time_zone = '+00:00'")
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


# MySQL-specific utilities
async def check_connection() -> bool:
    """
    Check if MySQL connection is healthy.

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
    Get MySQL server version.

    Returns:
        Version string or None if connection fails
    """
    try:
        async with async_engine.connect() as conn:
            result = await conn.execute(text("SELECT VERSION()"))
            row = result.fetchone()
            return row[0] if row else None
    except Exception:
        return None


async def get_database_size(database_name: str | None = None) -> str | None:
    """
    Get the size of the database.

    Args:
        database_name: Name of database (uses current if not specified)

    Returns:
        Human-readable database size or None if query fails
    """
    try:
        if database_name is None:
            query = text(
                "SELECT CONCAT(ROUND(SUM(data_length + index_length) / 1024 / 1024, 2), ' MB') "
                "FROM information_schema.tables WHERE table_schema = DATABASE()"
            )
        else:
            query = text(
                "SELECT CONCAT(ROUND(SUM(data_length + index_length) / 1024 / 1024, 2), ' MB') "
                f"FROM information_schema.tables WHERE table_schema = '{database_name}'"
            )
        async with async_engine.connect() as conn:
            result = await conn.execute(query)
            row = result.fetchone()
            return row[0] if row else None
    except Exception:
        return None


async def get_active_connections() -> int:
    """
    Get the number of active connections to the database.

    Returns:
        Number of active connections
    """
    try:
        async with async_engine.connect() as conn:
            result = await conn.execute(
                text("SELECT COUNT(*) FROM information_schema.processlist WHERE db = DATABASE()")
            )
            row = result.fetchone()
            return row[0] if row else 0
    except Exception:
        return 0


async def table_exists(table_name: str, database: str | None = None) -> bool:
    """
    Check if a table exists in the database.

    Args:
        table_name: Name of the table
        database: Database name (uses current if not specified)

    Returns:
        True if table exists, False otherwise
    """
    try:
        if database is None:
            query = text(
                "SELECT COUNT(*) FROM information_schema.tables "
                "WHERE table_schema = DATABASE() AND table_name = :table"
            )
        else:
            query = text(
                "SELECT COUNT(*) FROM information_schema.tables "
                "WHERE table_schema = :database AND table_name = :table"
            )
        async with async_engine.connect() as conn:
            result = await conn.execute(query, {"database": database, "table": table_name})
            row = result.fetchone()
            return (row[0] if row else 0) > 0
    except Exception:
        return False


async def get_table_row_count(table_name: str) -> int | None:
    """
    Get the approximate row count for a table.

    Args:
        table_name: Name of the table

    Returns:
        Approximate row count or None if query fails
    """
    try:
        async with async_engine.connect() as conn:
            result = await conn.execute(
                text(
                    "SELECT table_rows FROM information_schema.tables "
                    "WHERE table_schema = DATABASE() AND table_name = :table"
                ),
                {"table": table_name},
            )
            row = result.fetchone()
            return row[0] if row else None
    except Exception:
        return None


async def get_server_status() -> dict[str, Any]:
    """
    Get MySQL server status variables.

    Returns:
        Dictionary with server status information
    """
    try:
        async with async_engine.connect() as conn:
            result = await conn.execute(text("SHOW STATUS LIKE 'Threads%'"))
            rows = result.fetchall()
            return {row[0]: row[1] for row in rows}
    except Exception:
        return {}


# Connection pool statistics
def get_pool_status() -> dict[str, Any]:
    """
    Get connection pool statistics.

    Returns:
        Dictionary with pool status information
    """
    pool = engine.pool
    return {
        "pool_size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "invalid": pool.invalidated(),
    }


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
