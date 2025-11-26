"""
New Project Command
Creates a new FastAPI-New project with full directory structure.
"""

import pathlib
import shutil
import subprocess
from dataclasses import dataclass
from typing import Annotated

import typer
from rich_toolkit import RichToolkit

from fastapi_new.utils.cli import get_rich_toolkit
from fastapi_new.utils.templates import (
    copy_template_directory,
    create_project_context,
)


# Default dependencies for new projects
DEFAULT_DEPENDENCIES = [
    "fastapi[standard]",
    "sqlalchemy>=2.0.0",
    "pydantic-settings>=2.0.0",
    "python-jose[cryptography]",
    "passlib[bcrypt]",
    "aiosqlite",  # Default database driver
]


@dataclass
class ProjectConfig:
    name: str
    path: pathlib.Path
    python: str | None = None


def _generate_readme(project_name: str) -> str:
    """Generate a simple README for fallback."""
    return f"""# {project_name}

A FastAPI project built with FastAPI-New.

## Quick Start

```bash
# Start development server
uv run fastapi dev

# Create a new app module
fastapi-new createapp <app_name>
```

Visit http://localhost:8000/docs for API documentation.
"""


def _exit_with_error(toolkit: RichToolkit, error_msg: str) -> None:
    toolkit.print(f"[bold red]Error:[/bold red] {error_msg}", tag="error")
    raise typer.Exit(code=1)


def _validate_python_version(python: str | None) -> str | None:
    """
    Validate Python version is >= 3.10.
    Returns error message if < 3.10, None otherwise.
    """
    if not python:
        return None

    try:
        parts = python.split(".")
        if len(parts) < 2:
            return None  # Let uv handle malformed version
        major, minor = int(parts[0]), int(parts[1])

        if major < 3 or (major == 3 and minor < 10):
            return f"Python {python} is not supported. FastAPI requires Python 3.10 or higher."
    except (ValueError, IndexError):
        pass

    return None


def _setup_uv(toolkit: RichToolkit, config: ProjectConfig) -> None:
    """Initialize project with uv."""
    error = _validate_python_version(config.python)
    if error:
        _exit_with_error(toolkit, error)

    msg = "Setting up environment with uv"
    if config.python:
        msg += f" (Python {config.python})"

    toolkit.print(msg, tag="env")

    # Build init command
    if config.path == pathlib.Path.cwd():
        init_cmd = ["uv", "init", "--bare"]
    else:
        init_cmd = ["uv", "init", "--bare", config.name]

    if config.python:
        init_cmd.extend(["--python", config.python])

    try:
        subprocess.run(init_cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.decode() if e.stderr else "No details available"
        _exit_with_error(toolkit, f"Failed to initialize project with uv. {stderr}")


def _install_dependencies(toolkit: RichToolkit, config: ProjectConfig) -> None:
    """Install default dependencies."""
    toolkit.print("Installing dependencies...", tag="deps")

    for dep in DEFAULT_DEPENDENCIES:
        try:
            subprocess.run(
                ["uv", "add", dep],
                check=True,
                capture_output=True,
                cwd=config.path,
            )
            toolkit.print(f"  [green]✓[/green] {dep}")
        except subprocess.CalledProcessError as e:
            toolkit.print(f"  [yellow]⚠[/yellow] {dep} (failed)")


def _create_project_structure(toolkit: RichToolkit, config: ProjectConfig) -> None:
    """Create the full project structure from templates."""
    toolkit.print("Creating project structure...", tag="structure")

    # Create template context
    context = create_project_context(config.name)

    # Create app directory
    app_dir = config.path / "app"
    app_dir.mkdir(parents=True, exist_ok=True)

    # Copy all project templates
    try:
        created_files = copy_template_directory("project", app_dir, context)
        toolkit.print(f"  [green]✓[/green] Created {len(created_files)} files")
    except Exception as e:
        _exit_with_error(toolkit, f"Failed to create project structure: {e}")


def _create_env_file(toolkit: RichToolkit, config: ProjectConfig) -> None:
    """Create .env file from .env.example."""
    toolkit.print("Creating environment file...", tag="env")

    env_example = config.path / "app" / ".env.example"
    env_file = config.path / ".env"

    if env_example.exists():
        # Read and copy content
        content = env_example.read_text(encoding="utf-8")
        env_file.write_text(content, encoding="utf-8")

        # Also copy .env.example to project root
        (config.path / ".env.example").write_text(content, encoding="utf-8")

        # Remove from app directory
        env_example.unlink()

        toolkit.print("  [green]✓[/green] Created .env")
    else:
        # Create minimal .env
        env_content = f"""# {config.name} Environment Configuration
PROJECT_NAME={config.name}
ENVIRONMENT=dev
DEBUG=true
DATABASE_ENGINE=sqlite
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=change-this-in-production
"""
        env_file.write_text(env_content, encoding="utf-8")
        toolkit.print("  [green]✓[/green] Created .env (minimal)")


def _move_readme(toolkit: RichToolkit, config: ProjectConfig) -> None:
    """Move README.md to project root."""
    app_readme = config.path / "app" / "README.md"
    root_readme = config.path / "README.md"

    if app_readme.exists():
        # Read content and write to root
        content = app_readme.read_text(encoding="utf-8")
        root_readme.write_text(content, encoding="utf-8")
        # Remove from app directory
        app_readme.unlink()
    elif not root_readme.exists():
        # Create fallback README
        root_readme.write_text(_generate_readme(config.name), encoding="utf-8")


def _create_gitignore(toolkit: RichToolkit, config: ProjectConfig) -> None:
    """Create .gitignore file."""
    gitignore_path = config.path / ".gitignore"

    if gitignore_path.exists():
        return  # Don't overwrite existing

    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.env
.venv
env/
venv/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# Testing
.coverage
.pytest_cache/
htmlcov/
.tox/

# Database
*.db
*.sqlite
*.sqlite3

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db

# Project specific
.env
!.env.example
"""
    gitignore_path.write_text(gitignore_content, encoding="utf-8")


def new(
    ctx: typer.Context,
    project_name: Annotated[
        str | None,
        typer.Argument(
            help="The name of the new FastAPI project. If not provided, initializes in the current directory.",
        ),
    ] = None,
    python: Annotated[
        str | None,
        typer.Option(
            "--python",
            "-p",
            help="Specify the Python version for the new project (e.g., 3.14). Must be 3.10 or higher.",
        ),
    ] = None,
) -> None:
    """
    Create a new FastAPI-New project.

    Creates a complete project structure with:
        - MSSR architecture (Model, Schema, Service, Repository)
        - Auto-registration system
        - Database configuration
        - Security utilities
        - Shared exceptions and utilities
    """
    if project_name:
        name = project_name
        path = pathlib.Path.cwd() / project_name
    else:
        name = pathlib.Path.cwd().name
        path = pathlib.Path.cwd()

    config = ProjectConfig(
        name=name,
        path=path,
        python=python,
    )

    with get_rich_toolkit() as toolkit:
        toolkit.print_title("Creating a new FastAPI-New project 🚀", tag="FastAPI")
        toolkit.print_line()

        if not project_name:
            toolkit.print(
                f"[yellow]⚠️  No project name provided. Initializing in current directory: {path}[/yellow]",
                tag="warning",
            )
            toolkit.print_line()

        # Check if project directory already exists (only for new subdirectory)
        if project_name and config.path.exists():
            _exit_with_error(toolkit, f"Directory '{project_name}' already exists.")

        # Check for uv
        if shutil.which("uv") is None:
            _exit_with_error(
                toolkit,
                "uv is required to create new projects. Install it from https://docs.astral.sh/uv/getting-started/installation/",
            )

        # Step 1: Setup uv environment
        _setup_uv(toolkit, config)
        toolkit.print_line()

        # Step 2: Install dependencies
        _install_dependencies(toolkit, config)
        toolkit.print_line()

        # Step 3: Create project structure
        _create_project_structure(toolkit, config)
        toolkit.print_line()

        # Step 4: Create .env file
        _create_env_file(toolkit, config)

        # Step 5: Move README to root
        _move_readme(toolkit, config)

        # Step 6: Create .gitignore
        _create_gitignore(toolkit, config)

        toolkit.print_line()

        # Success message
        if project_name:
            toolkit.print(
                f"[bold green]✨ Success![/bold green] Created FastAPI-New project: [cyan]{project_name}[/cyan]",
                tag="success",
            )
            toolkit.print_line()

            toolkit.print("[bold]Project structure:[/bold]")
            toolkit.print(f"  {project_name}/")
            toolkit.print("  ├── app/")
            toolkit.print("  │   ├── main.py")
            toolkit.print("  │   ├── core/")
            toolkit.print("  │   ├── apps/")
            toolkit.print("  │   └── db/")
            toolkit.print("  ├── .env")
            toolkit.print("  └── pyproject.toml")

            toolkit.print_line()

            toolkit.print("[bold]Next steps:[/bold]")
            toolkit.print(f"  [dim]$[/dim] cd {project_name}")
            toolkit.print("  [dim]$[/dim] fastapi-new createapp users")
            toolkit.print("  [dim]$[/dim] uv run fastapi dev")
        else:
            toolkit.print(
                "[bold green]✨ Success![/bold green] Initialized FastAPI-New project in current directory",
                tag="success",
            )
            toolkit.print_line()

            toolkit.print("[bold]Next steps:[/bold]")
            toolkit.print("  [dim]$[/dim] fastapi-new createapp users")
            toolkit.print("  [dim]$[/dim] uv run fastapi dev")

        toolkit.print_line()
        toolkit.print("Visit [blue]http://localhost:8000/docs[/blue] for API documentation")
        toolkit.print_line()
        toolkit.print(
            "[dim]💡 Tip: Use 'fastapi-new createapp <name>' to generate app modules[/dim]"
        )
