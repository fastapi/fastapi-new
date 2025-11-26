"""
List Apps Command
Shows installed app modules in the project.
"""

import re
from pathlib import Path

import typer

from fastapi_new.utils.cli import get_rich_toolkit


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


def get_installed_apps(registry_path: Path) -> list[str]:
    """
    Read INSTALLED_APPS from registry.py.

    Args:
        registry_path: Path to registry.py

    Returns:
        List of registered app names
    """
    if not registry_path.exists():
        return []

    content = registry_path.read_text(encoding="utf-8")

    # Pattern to match INSTALLED_APPS list content
    pattern = r"INSTALLED_APPS\s*:\s*list\[str\]\s*=\s*\[(.*?)\]"
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        return []

    list_content = match.group(1)

    # Extract quoted strings
    apps = re.findall(r'["\'](\w+)["\']', list_content)
    return apps


def get_app_directories(apps_dir: Path) -> list[str]:
    """
    Get all app directories in app/apps/.

    Args:
        apps_dir: Path to apps directory

    Returns:
        List of app directory names
    """
    if not apps_dir.exists():
        return []

    apps = []
    for item in apps_dir.iterdir():
        if item.is_dir() and not item.name.startswith("_"):
            # Check if it has at least routes.py or __init__.py
            if (item / "__init__.py").exists() or (item / "routes.py").exists():
                apps.append(item.name)

    return sorted(apps)


def get_app_info(app_dir: Path) -> dict:
    """
    Get information about an app.

    Args:
        app_dir: Path to app directory

    Returns:
        Dictionary with app information
    """
    info = {
        "has_models": (app_dir / "models.py").exists(),
        "has_schemas": (app_dir / "schemas.py").exists(),
        "has_services": (app_dir / "services.py").exists(),
        "has_repositories": (app_dir / "repositories.py").exists(),
        "has_routes": (app_dir / "routes.py").exists(),
        "has_dependencies": (app_dir / "dependencies.py").exists(),
    }
    return info


def listapps(
    ctx: typer.Context,
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed information about each app",
    ),
) -> None:
    """
    List all installed app modules.

    Shows all apps in app/apps/ and their registration status.
    """
    with get_rich_toolkit() as toolkit:
        toolkit.print_title("Installed Apps 📋", tag="FastAPI")
        toolkit.print_line()

        # Find project root
        project_root = find_project_root()
        if project_root is None:
            toolkit.print(
                "[bold red]Error:[/bold red] Could not find project root. "
                "Make sure you're in a FastAPI-New project directory.",
                tag="error",
            )
            raise typer.Exit(code=1)

        # Get registered apps from INSTALLED_APPS
        registry_path = project_root / "app" / "core" / "registry.py"
        registered_apps = get_installed_apps(registry_path)

        # Get all app directories
        apps_dir = project_root / "app" / "apps"
        all_apps = get_app_directories(apps_dir)

        if not all_apps:
            toolkit.print(
                "[yellow]No apps found.[/yellow]",
                tag="info",
            )
            toolkit.print_line()
            toolkit.print("Create a new app with:")
            toolkit.print("  [dim]$[/dim] fastapi-new createapp <app_name>")
            raise typer.Exit(code=0)

        # Display apps
        toolkit.print(f"[bold]Apps directory:[/bold] {apps_dir.relative_to(project_root)}/")
        toolkit.print_line()

        registered_count = 0
        unregistered_count = 0

        for app_name in all_apps:
            is_registered = app_name in registered_apps

            if is_registered:
                status = "[green]✓ registered[/green]"
                registered_count += 1
            else:
                status = "[yellow]○ not registered[/yellow]"
                unregistered_count += 1

            toolkit.print(f"  [cyan]{app_name}[/cyan]  {status}")

            if verbose:
                app_info = get_app_info(apps_dir / app_name)
                files = []
                if app_info["has_models"]:
                    files.append("models")
                if app_info["has_schemas"]:
                    files.append("schemas")
                if app_info["has_services"]:
                    files.append("services")
                if app_info["has_repositories"]:
                    files.append("repositories")
                if app_info["has_routes"]:
                    files.append("routes")
                if app_info["has_dependencies"]:
                    files.append("dependencies")

                if files:
                    toolkit.print(f"    [dim]Files: {', '.join(files)}[/dim]")

        toolkit.print_line()

        # Summary
        total = len(all_apps)
        toolkit.print(f"[bold]Total:[/bold] {total} app(s)")
        toolkit.print(f"  [green]✓[/green] Registered: {registered_count}")
        if unregistered_count > 0:
            toolkit.print(f"  [yellow]○[/yellow] Not registered: {unregistered_count}")

        # Show hint for unregistered apps
        if unregistered_count > 0:
            toolkit.print_line()
            toolkit.print(
                "[dim]Tip: Add unregistered apps to INSTALLED_APPS in app/core/registry.py[/dim]"
            )
