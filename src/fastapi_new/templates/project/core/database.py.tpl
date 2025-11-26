"""
Database Configuration
Handles database connections, sessions, and engine management.
"""

from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings


# Sync engine configuration
def get_engine_args() -> dict[str, Any]:
    """Get engine arguments based on database type."""
    args: dict[str, Any] = {
        "echo": settings.DATABASE_ECHO,
    }

    if settings.DATABASE_ENGINE == "sqlite":
        # SQLite specific settings
        args["connect_args"] = {"check_same_thread": False}
        args["poolclass"] = StaticPool
    else:
        # PostgreSQL, MySQL connection pool settings
        args["pool_size"] = settings.DATABASE_POOL_SIZE
        args["max_overflow"] = settings.DATABASE_MAX_OVERFLOW
        args["pool_pre_ping"] = True

    return args


# Create sync engine
engine = create_engine(
    settings.DATABASE_URL,
    **get_engine_args(),
)

# Create sync session factory
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def get_async_database_url() -> str:
    """Convert sync database URL to async URL."""
    url = settings.DATABASE_URL

    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("mysql://"):
        return url.replace("mysql://", "mysql+aiomysql://", 1)
    elif url.startswith("sqlite://"):
        return url.replace("sqlite://", "sqlite+aiosqlite://", 1)

    return url


# Create async engine (if using async)
async_engine = create_async_engine(
    get_async_database_url(),
    echo=settings.DATABASE_ECHO,
    pool_pre_ping=True if settings.DATABASE_ENGINE != "sqlite" else False,
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


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
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


# SQLite specific: Enable foreign key constraints
if settings.DATABASE_ENGINE == "sqlite":
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection: Any, connection_record: Any) -> None:
        """Enable foreign key support for SQLite."""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


async def init_db() -> None:
    """
    Initialize database tables.
    Call this on application startup.
    """
    from app.db.base import Base

    async with async_engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    Close database connections.
    Call this on application shutdown.
    """
    await async_engine.dispose()


def init_db_sync() -> None:
    """
    Initialize database tables synchronously.
    Useful for scripts and migrations.
    """
    from app.db.base import Base

    Base.metadata.create_all(bind=engine)


def drop_db_sync() -> None:
    """
    Drop all database tables synchronously.
    WARNING: This will delete all data!
    """
    from app.db.base import Base

    Base.metadata.drop_all(bind=engine)
