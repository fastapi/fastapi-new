"""
Tests Module
Contains all test files for the application.

Test Structure:
    tests/
    ├── __init__.py
    ├── conftest.py         # Pytest fixtures and configuration
    ├── test_main.py        # Tests for main application
    └── apps/               # Tests for each app module
        ├── __init__.py
        └── test_<app_name>.py

Running Tests:
    # Run all tests
    uv run pytest

    # Run with coverage
    uv run pytest --cov=app

    # Run specific test file
    uv run pytest tests/test_main.py

    # Run with verbose output
    uv run pytest -v

Fixtures available in conftest.py:
    - client: TestClient for API testing
    - async_client: AsyncClient for async API testing
    - db_session: Database session for testing
    - test_user: Sample user fixture
"""
