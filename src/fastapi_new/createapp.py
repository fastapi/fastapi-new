"""
Create App Command
Generates a new MSSR (Model, Schema, Service, Repository) module.
"""

import re
import sys
from pathlib import Path
from typing import Annotated

import typer

from fastapi_new.utils.cli import get_rich_toolkit
from fastapi_new.utils.templates import (
    copy_template_directory,
    create_app_context,
    to_snake_case,
)


def find_project_root() -> Path | None:
    """
    Find the project root by looking for app/ directory.

    Returns:
        Path to project root or None if not found
    """
    current = Path.cwd()

    # Check current directory
    if (current / "app").is_dir():
        return current

    # Check parent directories (up to 3 levels)
    for _ in range(3):
        current = current.parent
        if (current / "app").is_dir():
            return current

    return None


def validate_app_name(name: str) -> str | None:
    """
    Validate app name.

    Args:
        name: App name to validate

    Returns:
        Error message if invalid, None if valid
    """
    # Convert to snake_case for validation
    name = to_snake_case(name)

    if not name:
        return "App name cannot be empty"

    if not re.match(r"^[a-z][a-z0-9_]*$", name):
        return "App name must start with a letter and contain only lowercase letters, numbers, and underscores"

    if name in ("app", "core", "db", "shared", "plugins", "tests"):
        return f"'{name}' is a reserved name"

    return None


def add_to_installed_apps(registry_path: Path, app_name: str) -> bool:
    """
    Add app to INSTALLED_APPS in registry.py.

    Args:
        registry_path: Path to registry.py
        app_name: Name of the app to add

    Returns:
        True if successful, False otherwise
    """
    if not registry_path.exists():
        return False

    content = registry_path.read_text(encoding="utf-8")

    # Check if already registered
    if f'"{app_name}"' in content or f"'{app_name}'" in content:
        return True  # Already registered

    # Find INSTALLED_APPS list and add the app
    # Pattern to match INSTALLED_APPS = [ ... ]
    pattern = r"(INSTALLED_APPS\s*:\s*list\[str\]\s*=\s*\[)(.*?)(\])"

    def replacer(match: re.Match) -> str:
        prefix = match.group(1)
        existing = match.group(2).strip()
        suffix = match.group(3)

        if existing and not existing.endswith(","):
            # Has existing items without trailing comma
            if existing.rstrip().endswith(("#", ",")):
                new_content = f'{existing}\n    "{app_name}",'
            else:
                new_content = f'{existing},\n    "{app_name}",'
        elif existing:
            # Has existing items with trailing comma or comments only
            new_content = f'{existing}\n    "{app_name}",'
        else:
            # Empty list
            new_content = f'\n    "{app_name}",\n'

        return f"{prefix}{new_content}\n{suffix}"

    new_content, count = re.subn(pattern, replacer, content, flags=re.DOTALL)

    if count > 0:
        registry_path.write_text(new_content, encoding="utf-8")
        return True

    return False


def createapp(
    ctx: typer.Context,
    app_name: Annotated[
        str,
        typer.Argument(
            help="Name of the app to create (e.g., users, products, orders)",
        ),
    ],
) -> None:
    """
    Create a new MSSR app module.

    Generates:
        - models.py: SQLAlchemy ORM models
        - schemas.py: Pydantic request/response schemas
        - services.py: Business logic layer
        - repositories.py: Data access layer
        - routes.py: API endpoints
        - dependencies.py: FastAPI dependencies
    """
    with get_rich_toolkit() as toolkit:
        toolkit.print_title("Creating new app module 📦", tag="FastAPI")
        toolkit.print_line()

        # Validate app name
        error = validate_app_name(app_name)
        if error:
            toolkit.print(f"[bold red]Error:[/bold red] {error}", tag="error")
            raise typer.Exit(code=1)

        # Normalize app name
        app_name_normalized = to_snake_case(app_name)

        # Find project root
        project_root = find_project_root()
        if project_root is None:
            toolkit.print(
                "[bold red]Error:[/bold red] Could not find project root. "
                "Make sure you're in a FastAPI-New project directory.",
                tag="error",
            )
            toolkit.print(
                "[dim]Hint: The project should have an 'app/' directory[/dim]"
            )
            raise typer.Exit(code=1)

        # Check if apps directory exists
        apps_dir = project_root / "app" / "apps"
        if not apps_dir.exists():
            toolkit.print(
                "[bold red]Error:[/bold red] 'app/apps/' directory not found. "
                "Is this a FastAPI-New project?",
                tag="error",
            )
            raise typer.Exit(code=1)

        # Check if app already exists
        app_dir = apps_dir / app_name_normalized
        if app_dir.exists():
            toolkit.print(
                f"[bold red]Error:[/bold red] App '{app_name_normalized}' already exists.",
                tag="error",
            )
            raise typer.Exit(code=1)

        toolkit.print(f"Creating app: [cyan]{app_name_normalized}[/cyan]", tag="app")
        toolkit.print_line()

        # Create template context
        context = create_app_context(app_name_normalized)

        # Create app directory and files
        try:
            toolkit.print("Generating MSSR module files...", tag="files")

            created_files = copy_template_directory("app", app_dir, context)

            for file_path in created_files:
                relative_path = file_path.relative_to(project_root)
                toolkit.print(f"  [green]✓[/green] {relative_path}")

        except Exception as e:
            toolkit.print(
                f"[bold red]Error:[/bold red] Failed to create app files: {e}",
                tag="error",
            )
            # Cleanup on failure
            if app_dir.exists():
                import shutil
                shutil.rmtree(app_dir)
            raise typer.Exit(code=1)

        toolkit.print_line()

        # Add to INSTALLED_APPS
        registry_path = project_root / "app" / "core" / "registry.py"
        if registry_path.exists():
            toolkit.print("Registering app in INSTALLED_APPS...", tag="registry")

            if add_to_installed_apps(registry_path, app_name_normalized):
                toolkit.print(
                    f"  [green]✓[/green] Added '{app_name_normalized}' to INSTALLED_APPS"
                )
            else:
                toolkit.print(
                    f"  [yellow]⚠[/yellow] Could not auto-register app. "
                    f"Please add '{app_name_normalized}' to INSTALLED_APPS manually."
                )

            toolkit.print_line()

        # Success message
        toolkit.print(
            f"[bold green]✨ Success![/bold green] Created app: [cyan]{app_name_normalized}[/cyan]",
            tag="success",
        )

        toolkit.print_line()

        toolkit.print("[bold]App structure:[/bold]")
        toolkit.print(f"  app/apps/{app_name_normalized}/")
        toolkit.print("  ├── __init__.py")
        toolkit.print("  ├── models.py")
        toolkit.print("  ├── schemas.py")
        toolkit.print("  ├── services.py")
        toolkit.print("  ├── repositories.py")
        toolkit.print("  ├── routes.py")
        toolkit.print("  └── dependencies.py")

        toolkit.print_line()

        toolkit.print("[bold]Next steps:[/bold]")
        toolkit.print(f"  1. Define your models in [cyan]app/apps/{app_name_normalized}/models.py[/cyan]")
        toolkit.print(f"  2. Create schemas in [cyan]app/apps/{app_name_normalized}/schemas.py[/cyan]")
        toolkit.print(f"  3. Add routes in [cyan]app/apps/{app_name_normalized}/routes.py[/cyan]")
        toolkit.print("  4. Run [dim]uv run fastapi dev[/dim] to start the server")
