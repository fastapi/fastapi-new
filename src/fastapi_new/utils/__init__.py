"""
FastAPI-New Utilities
"""

from fastapi_new.utils.cli import get_rich_toolkit
from fastapi_new.utils.templates import (
    copy_template_directory,
    copy_template_file,
    create_app_context,
    create_project_context,
    get_template_path,
    render_template,
    render_template_file,
    to_pascal_case,
    to_plural,
    to_singular,
    to_snake_case,
)

__all__ = [
    "get_rich_toolkit",
    "copy_template_directory",
    "copy_template_file",
    "create_app_context",
    "create_project_context",
    "get_template_path",
    "render_template",
    "render_template_file",
    "to_pascal_case",
    "to_plural",
    "to_singular",
    "to_snake_case",
]
