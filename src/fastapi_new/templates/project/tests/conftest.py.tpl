"""
Pytest Configuration and Fixtures
Provides reusable fixtures for testing the application.
"""

import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.db.base import Base
from app.main import app as main_app


# Test database URL (use in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite:///./test.db"
TEST_ASYNC_DATABASE_URL = "sqlite+aiosqlite:///./test.db"


# Sync test engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)

# Enable foreign keys for SQLite
@event.listens_for(test_engine, "connect")
def set_sqlite_pragma(dbapi_connection: Any, connection_record: Any) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# Sync test session factory
TestSessionLocal = sessionmaker(
    bind=test_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


# Async test engine
test_async_engine = create_async_engine(
    TEST_ASYNC_DATABASE_URL,
    echo=False,
)

# Async test session factory
TestAsyncSessionLocal = async_sessionmaker(
    bind=test_async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    Create a fresh database session for each test.
    Creates all tables before the test and drops them after.
    """
    # Create all tables
    Base.metadata.create_all(bind=test_engine)

    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
async def async_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a fresh async database session for each test.
    """
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestAsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
def app() -> FastAPI:
    """
    Get the FastAPI application instance.
    Override dependencies if needed.
    """
    return main_app


@pytest.fixture(scope="function")
def client(app: FastAPI, db_session: Session) -> Generator[TestClient, None, None]:
    """
    Create a test client for sync API testing.

    Usage:
        def test_endpoint(client):
            response = client.get("/api/v1/items")
            assert response.status_code == 200
    """
    # Override database dependency
    from app.db.session import get_db

    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Clear overrides
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def async_client(
    app: FastAPI, async_db_session: AsyncSession
) -> AsyncGenerator[AsyncClient, None]:
    """
    Create an async test client for async API testing.

    Usage:
        async def test_endpoint(async_client):
            response = await async_client.get("/api/v1/items")
            assert response.status_code == 200
    """
    # Override database dependency
    from app.db.session import get_async_db

    async def override_get_async_db() -> AsyncGenerator[AsyncSession, None]:
        yield async_db_session

    app.dependency_overrides[get_async_db] = override_get_async_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    # Clear overrides
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def auth_headers() -> dict[str, str]:
    """
    Generate authentication headers for testing protected endpoints.

    Usage:
        def test_protected_endpoint(client, auth_headers):
            response = client.get("/api/v1/protected", headers=auth_headers)
            assert response.status_code == 200
    """
    from app.core.security import create_access_token

    # Create a test token
    token = create_access_token(
        subject="test-user-id",
        roles=["user"],
        scopes=["read", "write"],
    )

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def admin_auth_headers() -> dict[str, str]:
    """
    Generate admin authentication headers for testing admin endpoints.
    """
    from app.core.security import create_access_token

    token = create_access_token(
        subject="admin-user-id",
        roles=["admin", "user"],
        scopes=["read", "write", "admin"],
    )

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def mock_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Override settings for testing.

    Usage:
        def test_with_custom_settings(mock_settings, monkeypatch):
            monkeypatch.setattr(settings, "DEBUG", True)
            # Your test code
    """
    # Set test-specific settings
    monkeypatch.setattr(settings, "ENVIRONMENT", "test")
    monkeypatch.setattr(settings, "DEBUG", True)
    monkeypatch.setattr(settings, "DATABASE_URL", TEST_DATABASE_URL)


# Sample data fixtures
@pytest.fixture(scope="function")
def sample_user_data() -> dict[str, Any]:
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User",
    }


@pytest.fixture(scope="function")
def sample_item_data() -> dict[str, Any]:
    """Sample item data for testing."""
    return {
        "name": "Test Item",
        "description": "A test item description",
        "price": 99.99,
        "is_active": True,
    }


# Helper functions
def create_test_user(db: Session, **kwargs: Any) -> Any:
    """
    Helper function to create a test user.
    Implement based on your User model.
    """
    # Example implementation:
    # from app.apps.users.models import User
    # from app.core.security import hash_password
    #
    # user = User(
    #     email=kwargs.get("email", "test@example.com"),
    #     hashed_password=hash_password(kwargs.get("password", "password123")),
    #     is_active=True,
    # )
    # db.add(user)
    # db.commit()
    # db.refresh(user)
    # return user
    pass


async def create_test_user_async(db: AsyncSession, **kwargs: Any) -> Any:
    """
    Async helper function to create a test user.
    """
    # Implement based on your User model
    pass
