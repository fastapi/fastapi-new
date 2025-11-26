"""
Doctor Command
Diagnoses project structure and configuration.
"""

from pathlib import Path

import typer

from fastapi_new.utils.cli import get_rich_toolkit


# Required project structure
REQUIRED_DIRS = [
    "app",
    "app/core",
    "app/apps",
    "app/db",
]

REQUIRED_CORE_FILES = [
    "app/core/config.py",
    "app/core/registry.py",
    "app/core/database.py",
]

OPTIONAL_CORE_FILES = [
    "app/core/security.py",
    "app/core/container.py",
]

REQUIRED_DB_FILES = [
    "app/db/base.py",
    "app/db/session.py",
]




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


def check_directories(project_root: Path) -> list[tuple[str, bool, str]]:
    """
    Check required directories exist.

    Returns:
        List of (path, exists, message) tuples
    """
    results = []
    for dir_path in REQUIRED_DIRS:
        full_path = project_root / dir_path
        exists = full_path.is_dir()
        msg = "OK" if exists else "Missing"
        results.append((dir_path, exists, msg))
    return results


def check_files(project_root: Path, files: list[str], required: bool = True) -> list[tuple[str, bool, str]]:
    """
    Check files exist.

    Returns:
        List of (path, exists, message) tuples
    """
    results = []
    for file_path in files:
        full_path = project_root / file_path
        exists = full_path.is_file()
        if exists:
            msg = "OK"
        elif required:
            msg = "Missing (required)"
        else:
            msg = "Missing (optional)"
        results.append((file_path, exists, msg))
    return results


def check_installed_apps(project_root: Path) -> list[tuple[str, bool, str]]:
    """
    Check that all INSTALLED_APPS have valid app directories.

    Returns:
        List of (app_name, valid, message) tuples
    """
    import re

    results = []
    registry_path = project_root / "app" / "core" / "registry.py"

    if not registry_path.exists():
        return [("registry.py", False, "File not found")]

    content = registry_path.read_text(encoding="utf-8")

    # Extract INSTALLED_APPS
    pattern = r"INSTALLED_APPS\s*:\s*list\[str\]\s*=\s*\[(.*?)\]"
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        return [("INSTALLED_APPS", False, "Could not parse INSTALLED_APPS")]

    list_content = match.group(1)
    
    # Only find apps that are not commented out
    # Split by lines and filter out commented lines
    apps = []
    for line in list_content.split('\n'):
        # Skip empty lines and lines starting with # (comments)
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        # Extract app names from non-commented lines
        app_matches = re.findall(r'["\'](\w+)["\']', line)
        apps.extend(app_matches)

    if not apps:
        results.append(("INSTALLED_APPS", True, "Empty (no apps registered)"))
        return results

    apps_dir = project_root / "app" / "apps"
    for app_name in apps:
        app_path = apps_dir / app_name
        if app_path.is_dir():
            # Check for routes.py
            if (app_path / "routes.py").exists():
                results.append((app_name, True, "OK"))
            else:
                results.append((app_name, False, "Missing routes.py"))
        else:
            results.append((app_name, False, "Directory not found"))

    return results


def check_env_file(project_root: Path) -> list[tuple[str, bool, str]]:
    """
    Check environment configuration.

    Returns:
        List of (item, ok, message) tuples
    """
    results = []

    env_file = project_root / ".env"
    env_example = project_root / ".env.example"

    if env_file.exists():
        results.append((".env", True, "OK"))

        # Check for required vars
        content = env_file.read_text(encoding="utf-8")
        if "DATABASE_URL=" in content:
            results.append(("DATABASE_URL", True, "Configured"))
        else:
            results.append(("DATABASE_URL", False, "Not set"))

        if "SECRET_KEY=" in content:
            # Check if it's the default
            if "change-in-production" in content or "change-this-in-production" in content or "your-secret-key" in content:
                results.append(("SECRET_KEY", False, "Using default (change for production)"))
            else:
                results.append(("SECRET_KEY", True, "Configured"))
        else:
            results.append(("SECRET_KEY", False, "Not set"))
    else:
        results.append((".env", False, "Not found"))
        if env_example.exists():
            results.append((".env.example", True, "Available (copy to .env)"))

    return results


def check_main_py(project_root: Path) -> tuple[bool, str]:
    """
    Check main.py exists and has required structure.

    Returns:
        (ok, message) tuple
    """
    main_py = project_root / "app" / "main.py"

    if not main_py.exists():
        return False, "Not found"

    content = main_py.read_text(encoding="utf-8")

    # Check for FastAPI import first
    if "FastAPI" not in content:
        return False, "FastAPI not imported"

    # Check for app instance
    if "app = " not in content and "app=" not in content:
        return False, "No app instance found"

    return True, "OK"


def doctor(
    ctx: typer.Context,
) -> None:
    """
    Diagnose project structure and configuration.

    Checks:
        - Required directories exist
        - Core files are present
        - INSTALLED_APPS are valid
        - Environment is configured
    """
    with get_rich_toolkit() as toolkit:
        toolkit.print_title("Project Diagnosis 🩺", tag="FastAPI")
        toolkit.print_line()

        # Find project root
        project_root = find_project_root()
        if project_root is None:
            toolkit.print(
                "[bold red]Error:[/bold red] Could not find project root.",
                tag="error",
            )
            toolkit.print("[dim]Make sure you're in a FastAPI-New project directory[/dim]")
            raise typer.Exit(code=1)

        toolkit.print(f"[bold]Project root:[/bold] {project_root}")
        toolkit.print_line()

        issues = 0
        warnings = 0

        # Check directories
        toolkit.print("[bold]Directories:[/bold]", tag="check")
        dir_results = check_directories(project_root)
        for path, ok, msg in dir_results:
            if ok:
                toolkit.print(f"  [green]✓[/green] {path}")
            else:
                toolkit.print(f"  [red]✗[/red] {path} - {msg}")
                issues += 1

        toolkit.print_line()

        # Check core files
        toolkit.print("[bold]Core files:[/bold]", tag="check")
        core_results = check_files(project_root, REQUIRED_CORE_FILES, required=True)
        core_results += check_files(project_root, OPTIONAL_CORE_FILES, required=False)
        for path, ok, msg in core_results:
            if ok:
                toolkit.print(f"  [green]✓[/green] {path}")
            elif "optional" in msg.lower():
                toolkit.print(f"  [yellow]○[/yellow] {path} - {msg}")
            else:
                toolkit.print(f"  [red]✗[/red] {path} - {msg}")
                issues += 1

        toolkit.print_line()

        # Check main.py
        toolkit.print("[bold]Main application:[/bold]", tag="check")
        main_ok, main_msg = check_main_py(project_root)
        if main_ok:
            toolkit.print(f"  [green]✓[/green] app/main.py - {main_msg}")
        else:
            toolkit.print(f"  [red]✗[/red] app/main.py - {main_msg}")
            issues += 1

        toolkit.print_line()

        # Check database files
        toolkit.print("[bold]Database files:[/bold]", tag="check")
        db_results = check_files(project_root, REQUIRED_DB_FILES, required=True)
        for path, ok, msg in db_results:
            if ok:
                toolkit.print(f"  [green]✓[/green] {path}")
            else:
                toolkit.print(f"  [red]✗[/red] {path} - {msg}")
                issues += 1

        toolkit.print_line()

        # Check INSTALLED_APPS
        toolkit.print("[bold]Installed apps:[/bold]", tag="check")
        app_results = check_installed_apps(project_root)
        for name, ok, msg in app_results:
            if ok:
                toolkit.print(f"  [green]✓[/green] {name} - {msg}")
            else:
                toolkit.print(f"  [red]✗[/red] {name} - {msg}")
                issues += 1

        toolkit.print_line()

        # Check environment
        toolkit.print("[bold]Environment:[/bold]", tag="check")
        env_results = check_env_file(project_root)
        for name, ok, msg in env_results:
            if ok:
                toolkit.print(f"  [green]✓[/green] {name} - {msg}")
            elif "default" in msg.lower() or "optional" in msg.lower():
                toolkit.print(f"  [yellow]⚠[/yellow] {name} - {msg}")
                warnings += 1
            else:
                toolkit.print(f"  [red]✗[/red] {name} - {msg}")
                issues += 1

        toolkit.print_line()

        # Summary
        if issues == 0 and warnings == 0:
            toolkit.print(
                "[bold green]✨ All checks passed![/bold green] Your project looks healthy.",
                tag="result",
            )
        elif issues == 0:
            toolkit.print(
                f"[bold yellow]⚠ {warnings} warning(s)[/bold yellow] - Project is functional but has minor issues.",
                tag="result",
            )
        else:
            toolkit.print(
                f"[bold red]✗ {issues} issue(s)[/bold red], {warnings} warning(s)",
                tag="result",
            )
            toolkit.print_line()
            toolkit.print("[bold]Suggestions:[/bold]")
            toolkit.print("  • Run [dim]fastapi-new createapp <name>[/dim] to create missing apps")
            toolkit.print("  • Copy .env.example to .env and configure settings")
            toolkit.print("  • Ensure all INSTALLED_APPS have a routes.py file")
