"""
{{project_name}} - FastAPI Application
Generated with FastAPI-New
"""

from contextlib import asynccontextmanager
from importlib import import_module
from typing import AsyncGenerator

from fastapi import FastAPI

from app.core.config import settings
from app.core.registry import INSTALLED_APPS


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    print(f"🚀 Starting {settings.PROJECT_NAME}...")

    # Initialize database connections
    # from app.db.session import engine
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)

    yield

    # Shutdown
    print(f"👋 Shutting down {settings.PROJECT_NAME}...")


def create_app() -> FastAPI:
    """
    Application factory pattern.
    Creates and configures the FastAPI application.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json" if settings.OPENAPI_URL else None,
        docs_url="/docs" if settings.DOCS_URL else None,
        redoc_url="/redoc" if settings.REDOC_URL else None,
        lifespan=lifespan,
    )

    # Register all installed apps
    register_apps(app)

    return app


def register_apps(app: FastAPI) -> None:
    """
    Auto-register all installed apps from INSTALLED_APPS.
    Each app must have a routes.py with a 'router' object.
    """
    for module_name in INSTALLED_APPS:
        try:
            module = import_module(f"app.apps.{module_name}.routes")
            if hasattr(module, "router"):
                app.include_router(
                    module.router,
                    prefix=f"{settings.API_V1_PREFIX}/{module_name}",
                    tags=[module_name.capitalize()],
                )
                print(f"  ✓ Registered app: {module_name}")
            else:
                print(f"  ⚠ App '{module_name}' has no router")
        except ImportError as e:
            print(f"  ✗ Failed to load app '{module_name}': {e}")


app = create_app()


@app.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
