"""
Core Module
Contains application configuration, database, security, and dependency injection.
"""

from app.core.config import settings, get_settings
from app.core.registry import INSTALLED_APPS, INSTALLED_PLUGINS

__all__ = [
    "settings",
    "get_settings",
    "INSTALLED_APPS",
    "INSTALLED_PLUGINS",
]
