"""
Template Engine Utility
Handles processing of .tpl template files for project and app generation.
"""

import os
import re
import shutil
from pathlib import Path
from typing import Any


# Path to templates directory
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def get_template_path(template_type: str) -> Path:
    """
    Get the path to a template directory.

    Args:
        template_type: Type of template ('project', 'app', 'db')

    Returns:
        Path to the template directory
    """
    return TEMPLATES_DIR / template_type


def render_template(content: str, context: dict[str, Any]) -> str:
    """
    Render template content by replacing {{variable}} placeholders.

    Args:
        content: Template content with {{variable}} placeholders
        context: Dictionary of variable names to values

    Returns:
        Rendered content with placeholders replaced
    """
    def replace_var(match: re.Match) -> str:
        var_name = match.group(1)
        return str(context.get(var_name, match.group(0)))

    # Replace {{variable_name}} patterns
    pattern = r"\{\{(\w+)\}\}"
    return re.sub(pattern, replace_var, content)


def render_template_file(template_path: Path, context: dict[str, Any]) -> str:
    """
    Read and render a template file.

    Args:
        template_path: Path to the .tpl template file
        context: Dictionary of variable names to values

    Returns:
        Rendered content
    """
    content = template_path.read_text(encoding="utf-8")
    return render_template(content, context)


def copy_template_file(
    template_path: Path,
    destination_path: Path,
    context: dict[str, Any],
) -> None:
    """
    Copy and render a single template file to destination.

    Args:
        template_path: Path to the .tpl template file
        destination_path: Destination path (without .tpl extension)
        context: Dictionary of variable names to values
    """
    # Ensure parent directory exists
    destination_path.parent.mkdir(parents=True, exist_ok=True)

    # Render and write content
    rendered_content = render_template_file(template_path, context)
    destination_path.write_text(rendered_content, encoding="utf-8")


def copy_template_directory(
    template_type: str,
    destination: Path,
    context: dict[str, Any],
) -> list[Path]:
    """
    Copy and render all template files from a template directory.

    Args:
        template_type: Type of template ('project', 'app', 'db')
        destination: Destination directory
        context: Dictionary of variable names to values

    Returns:
        List of created file paths
    """
    template_dir = get_template_path(template_type)
    created_files: list[Path] = []

    for template_path in template_dir.rglob("*.tpl"):
        # Calculate relative path from template directory
        relative_path = template_path.relative_to(template_dir)

        # Remove .tpl extension for destination
        dest_relative = Path(str(relative_path)[:-4])  # Remove .tpl

        # Full destination path
        dest_path = destination / dest_relative

        # Copy and render the file
        copy_template_file(template_path, dest_path, context)
        created_files.append(dest_path)

    return created_files


def to_pascal_case(text: str) -> str:
    """
    Convert text to PascalCase.

    Args:
        text: Input text (snake_case, kebab-case, or space-separated)

    Returns:
        PascalCase string

    Examples:
        to_pascal_case("users") -> "Users"
        to_pascal_case("user_profile") -> "UserProfile"
        to_pascal_case("order-items") -> "OrderItems"
    """
    # Split by underscores, hyphens, or spaces
    words = re.split(r"[_\-\s]+", text)
    return "".join(word.capitalize() for word in words if word)


def to_snake_case(text: str) -> str:
    """
    Convert text to snake_case.

    Args:
        text: Input text (PascalCase, camelCase, kebab-case, or space-separated)

    Returns:
        snake_case string

    Examples:
        to_snake_case("UserProfile") -> "user_profile"
        to_snake_case("orderItems") -> "order_items"
    """
    # Handle PascalCase/camelCase
    text = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", text)
    text = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", text)
    # Replace hyphens and spaces with underscores
    text = re.sub(r"[-\s]+", "_", text)
    return text.lower()


def to_singular(text: str) -> str:
    """
    Convert plural word to singular (simple implementation).

    Args:
        text: Plural word

    Returns:
        Singular form

    Examples:
        to_singular("users") -> "user"
        to_singular("categories") -> "category"
        to_singular("items") -> "item"
    """
    if text.endswith("ies"):
        return text[:-3] + "y"
    elif text.endswith("es") and text[-3] in "sxz":
        return text[:-2]
    elif text.endswith("s") and not text.endswith("ss"):
        return text[:-1]
    return text


def to_plural(text: str) -> str:
    """
    Convert singular word to plural (simple implementation).

    Args:
        text: Singular word

    Returns:
        Plural form

    Examples:
        to_plural("user") -> "users"
        to_plural("category") -> "categories"
    """
    if text.endswith("y") and text[-2] not in "aeiou":
        return text[:-1] + "ies"
    elif text.endswith(("s", "x", "z", "ch", "sh")):
        return text + "es"
    return text + "s"


def create_app_context(app_name: str) -> dict[str, str]:
    """
    Create template context for app generation.

    Args:
        app_name: Name of the app (e.g., "users", "order_items")

    Returns:
        Dictionary with template variables
    """
    # Normalize app name to snake_case
    app_name_snake = to_snake_case(app_name)

    # Get singular form for model name
    app_name_singular = to_singular(app_name_snake)

    return {
        "app_name": app_name_snake,
        "app_name_pascal": to_pascal_case(app_name_snake),
        "model_name": to_pascal_case(app_name_singular),
        "table_name": app_name_snake,
        "app_description": f"{to_pascal_case(app_name_snake)} module",
    }


def create_project_context(project_name: str) -> dict[str, str]:
    """
    Create template context for project generation.

    Args:
        project_name: Name of the project

    Returns:
        Dictionary with template variables
    """
    return {
        "project_name": project_name,
        "project_name_snake": to_snake_case(project_name),
        "project_name_pascal": to_pascal_case(project_name),
    }
