"""
Application Registry
Manages installed apps similar to Django's INSTALLED_APPS.

Add your app names to INSTALLED_APPS to auto-register them with FastAPI.
"""

from typing import Any

# List of installed applications
# Add your app names here to auto-register their routes
# Example: INSTALLED_APPS = ["users", "products", "orders"]
INSTALLED_APPS: list[str] = [
    # Add your apps here
    # "users",
    # "products",
]

# Plugin registry for dynamic plugin loading
INSTALLED_PLUGINS: list[str] = [
    # Add your plugins here
    # "auth",
    # "notifications",
]

# Registry for storing app metadata
_app_registry: dict[str, dict[str, Any]] = {}


def register_app(name: str, metadata: dict[str, Any] | None = None) -> None:
    """
    Register an app in the registry.

    Args:
        name: The app name
        metadata: Optional metadata about the app
    """
    _app_registry[name] = metadata or {}


def unregister_app(name: str) -> None:
    """
    Unregister an app from the registry.

    Args:
        name: The app name to unregister
    """
    if name in _app_registry:
        del _app_registry[name]


def get_app_metadata(name: str) -> dict[str, Any] | None:
    """
    Get metadata for a registered app.

    Args:
        name: The app name

    Returns:
        The app metadata or None if not registered
    """
    return _app_registry.get(name)


def get_registered_apps() -> list[str]:
    """
    Get list of all registered apps.

    Returns:
        List of registered app names
    """
    return list(_app_registry.keys())


def is_app_registered(name: str) -> bool:
    """
    Check if an app is registered.

    Args:
        name: The app name

    Returns:
        True if registered, False otherwise
    """
    return name in _app_registry


def get_all_apps() -> list[str]:
    """
    Get all apps from INSTALLED_APPS.

    Returns:
        List of all installed app names
    """
    return INSTALLED_APPS.copy()


def add_app(name: str) -> bool:
    """
    Add an app to INSTALLED_APPS dynamically.
    Note: This only affects runtime, not the file.

    Args:
        name: The app name to add

    Returns:
        True if added, False if already exists
    """
    if name not in INSTALLED_APPS:
        INSTALLED_APPS.append(name)
        return True
    return False


def remove_app(name: str) -> bool:
    """
    Remove an app from INSTALLED_APPS dynamically.
    Note: This only affects runtime, not the file.

    Args:
        name: The app name to remove

    Returns:
        True if removed, False if not found
    """
    if name in INSTALLED_APPS:
        INSTALLED_APPS.remove(name)
        return True
    return False
