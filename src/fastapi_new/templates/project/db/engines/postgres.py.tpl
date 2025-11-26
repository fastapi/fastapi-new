"""
PostgreSQL Database Engine Configuration
Provides PostgreSQL-specific database setup and utilities.
"""

from typing import Any

from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool

from app.core.config import settings


def get_postgres_url(async_mode: bool = False) -> str:
    """
    Get PostgreSQL connection URL.

    Args:
        async_mode: If True, returns asyncpg URL; otherwise returns psycopg2 URL

    Returns:
        PostgreSQL connection string
    """
    url = settings.DATABASE_URL

    if async_mode:
        # Convert to async driver
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+asyncpg://", 1)
    else:
        # Ensure sync driver
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql://", 1)

    return url


def get_engine_options() -> dict[str, Any]:
    """
    Get PostgreSQL engine options optimized for production.

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
            # "options": "-c timezone=utc",  # Set timezone to UTC
        },
    }


def get_async_engine_options() -> dict[str, Any]:
    """
    Get PostgreSQL async engine options.

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
    get_postgres_url(async_mode=False),
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
    get_postgres_url(async_mode=True),
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


# PostgreSQL-specific utilities
async def check_connection() -> bool:
    """
    Check if PostgreSQL connection is healthy.

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
    Get PostgreSQL server version.

    Returns:
        Version string or None if connection fails
    """
    try:
        async with async_engine.connect() as conn:
            result = await conn.execute(text("SELECT version()"))
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
        query = text(
            "SELECT pg_size_pretty(pg_database_size(current_database()))"
            if database_name is None
            else f"SELECT pg_size_pretty(pg_database_size('{database_name}'))"
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
                text(
                    "SELECT count(*) FROM pg_stat_activity "
                    "WHERE datname = current_database()"
                )
            )
            row = result.fetchone()
            return row[0] if row else 0
    except Exception:
        return 0


async def table_exists(table_name: str, schema: str = "public") -> bool:
    """
    Check if a table exists in the database.

    Args:
        table_name: Name of the table
        schema: Schema name (default: public)

    Returns:
        True if table exists, False otherwise
    """
    try:
        async with async_engine.connect() as conn:
            result = await conn.execute(
                text(
                    "SELECT EXISTS ("
                    "SELECT FROM information_schema.tables "
                    "WHERE table_schema = :schema AND table_name = :table"
                    ")"
                ),
                {"schema": schema, "table": table_name},
            )
            row = result.fetchone()
            return row[0] if row else False
    except Exception:
        return False


def configure_search_path(schema: str = "public") -> None:
    """
    Configure the default search path for the connection.

    Args:
        schema: Schema to set as search path
    """
    @event.listens_for(engine, "connect")
    def set_search_path(dbapi_connection: Any, connection_record: Any) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute(f"SET search_path TO {schema}")
        cursor.close()


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
