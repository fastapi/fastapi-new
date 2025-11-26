"""
Database Session Management
Provides session utilities and context managers for database operations.
"""

from collections.abc import AsyncGenerator, Generator
from contextlib import asynccontextmanager, contextmanager
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.database import AsyncSessionLocal, SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Sync database session dependency for FastAPI.

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
    Async database session dependency for FastAPI.

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


@contextmanager
def db_session() -> Generator[Session, None, None]:
    """
    Context manager for sync database sessions.

    Usage:
        with db_session() as db:
            user = db.query(User).first()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@asynccontextmanager
async def async_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for async database sessions.

    Usage:
        async with async_db_session() as db:
            result = await db.execute(select(User))
            user = result.scalar_one_or_none()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


class TransactionManager:
    """
    Transaction manager for complex operations spanning multiple repositories.

    Usage:
        async with TransactionManager() as tx:
            await user_repo.create(tx.session, user_data)
            await profile_repo.create(tx.session, profile_data)
            # Commits on successful exit, rolls back on exception
    """

    def __init__(self) -> None:
        self.session: AsyncSession | None = None

    async def __aenter__(self) -> "TransactionManager":
        self.session = AsyncSessionLocal()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        if self.session is None:
            return

        try:
            if exc_type is not None:
                await self.session.rollback()
            else:
                await self.session.commit()
        finally:
            await self.session.close()

    async def commit(self) -> None:
        """Manually commit the transaction."""
        if self.session:
            await self.session.commit()

    async def rollback(self) -> None:
        """Manually rollback the transaction."""
        if self.session:
            await self.session.rollback()


class SyncTransactionManager:
    """
    Sync transaction manager for complex operations.

    Usage:
        with SyncTransactionManager() as tx:
            user_repo.create(tx.session, user_data)
            profile_repo.create(tx.session, profile_data)
    """

    def __init__(self) -> None:
        self.session: Session | None = None

    def __enter__(self) -> "SyncTransactionManager":
        self.session = SessionLocal()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        if self.session is None:
            return

        try:
            if exc_type is not None:
                self.session.rollback()
            else:
                self.session.commit()
        finally:
            self.session.close()

    def commit(self) -> None:
        """Manually commit the transaction."""
        if self.session:
            self.session.commit()

    def rollback(self) -> None:
        """Manually rollback the transaction."""
        if self.session:
            self.session.rollback()


# Type aliases for convenience
DBSession = Session
AsyncDBSession = AsyncSession
