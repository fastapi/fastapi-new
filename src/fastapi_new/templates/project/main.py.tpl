"""
{{project_name}} - FastAPI Application

A minimal FastAPI project with modular structure.
Add your apps using: fastapi-new createapp <name>
"""

from importlib import import_module

from fastapi import FastAPI

from app.core.config import settings
from app.core.registry import INSTALLED_APPS


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.VERSION,
    )

    # Auto-register all app modules from INSTALLED_APPS
    for app_name in INSTALLED_APPS:
        try:
            routes = import_module(f"app.apps.{app_name}.routes")
            if hasattr(routes, "router"):
                app.include_router(
                    routes.router,
                    prefix=f"/api/v1/{app_name}",
                    tags=[app_name.capitalize()],
                )
                print(f"✓ Registered: {app_name}")
        except ImportError as e:
            print(f"⚠ Could not load {app_name}: {e}")

    return app


app = create_app()


@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}
