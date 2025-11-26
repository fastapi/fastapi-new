"""
Add Database Command
Adds database engine support to the project.
"""

import re
from pathlib import Path
from typing import Annotated

import typer

from fastapi_new.utils.cli import get_rich_toolkit


SUPPORTED_ENGINES = {
    "postgres": {
        "name": "PostgreSQL",
        "dependencies": ["asyncpg", "psycopg2-binary"],
        "url_example": "postgresql://user:password@localhost:5432/dbname",
    },
    "mysql": {
        "name": "MySQL",
        "dependencies": ["aiomysql", "pymysql"],
        "url_example": "mysql://user:password@localhost:3306/dbname",
    },
    "sqlite": {
        "name": "SQLite",
        "dependencies": ["aiosqlite"],
        "url_example": "sqlite:///./app.db",
    },
    "mongodb": {
        "name": "MongoDB",
        "dependencies": ["motor", "pymongo"],
        "url_example": "mongodb://user:password@localhost:27017/dbname",
    },
}


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


def update_config_engine(config_path: Path, engine: str) -> bool:
    """
    Update DATABASE_ENGINE in config.py.

    Args:
        config_path: Path to config.py
        engine: Database engine name

    Returns:
        True if successful, False otherwise
    """
    if not config_path.exists():
        return False

    content = config_path.read_text(encoding="utf-8")

    # Update DATABASE_ENGINE setting
    pattern = r'(DATABASE_ENGINE\s*:\s*.*?=\s*)["\'](\w+)["\']'
    new_content = re.sub(pattern, f'\\1"{engine}"', content)

    if new_content != content:
        config_path.write_text(new_content, encoding="utf-8")
        return True

    return False


def update_env_file(env_path: Path, engine: str, url_example: str) -> bool:
    """
    Update .env file with database settings.

    Args:
        env_path: Path to .env file
        engine: Database engine name
        url_example: Example database URL

    Returns:
        True if successful, False otherwise
    """
    if not env_path.exists():
        # Create .env from .env.example if it exists
        env_example = env_path.parent / ".env.example"
        if env_example.exists():
            content = env_example.read_text(encoding="utf-8")
        else:
            content = ""
    else:
        content = env_path.read_text(encoding="utf-8")

    updated = False

    # Update DATABASE_ENGINE
    if "DATABASE_ENGINE=" in content:
        content = re.sub(
            r"DATABASE_ENGINE=\w*",
            f"DATABASE_ENGINE={engine}",
            content,
        )
        updated = True
    else:
        content += f"\nDATABASE_ENGINE={engine}\n"
        updated = True

    # Update DATABASE_URL if sqlite
    if engine == "sqlite" and "DATABASE_URL=" in content:
        content = re.sub(
            r"DATABASE_URL=.*",
            f"DATABASE_URL={url_example}",
            content,
        )

    if updated:
        env_path.write_text(content, encoding="utf-8")
        return True

    return False


def adddb(
    ctx: typer.Context,
    engine: Annotated[
        str,
        typer.Argument(
            help="Database engine to add (postgres, mysql, sqlite, mongodb)",
        ),
    ],
    install: Annotated[
        bool,
        typer.Option(
            "--install",
            "-i",
            help="Install database dependencies with uv",
        ),
    ] = False,
) -> None:
    """
    Add database engine support to the project.

    Supported engines:
        - postgres: PostgreSQL with asyncpg
        - mysql: MySQL with aiomysql
        - sqlite: SQLite with aiosqlite (default)
        - mongodb: MongoDB with motor
    """
    with get_rich_toolkit() as toolkit:
        toolkit.print_title("Adding database engine 🗄️", tag="FastAPI")
        toolkit.print_line()

        # Normalize engine name
        engine = engine.lower().strip()

        # Handle aliases
        if engine == "postgresql":
            engine = "postgres"
        elif engine == "mongo":
            engine = "mongodb"

        # Validate engine
        if engine not in SUPPORTED_ENGINES:
            toolkit.print(
                f"[bold red]Error:[/bold red] Unknown database engine: '{engine}'",
                tag="error",
            )
            toolkit.print_line()
            toolkit.print("[bold]Supported engines:[/bold]")
            for eng, info in SUPPORTED_ENGINES.items():
                toolkit.print(f"  • {eng} ({info['name']})")
            raise typer.Exit(code=1)

        engine_info = SUPPORTED_ENGINES[engine]

        # Find project root
        project_root = find_project_root()
        if project_root is None:
            toolkit.print(
                "[bold red]Error:[/bold red] Could not find project root. "
                "Make sure you're in a FastAPI-New project directory.",
                tag="error",
            )
            raise typer.Exit(code=1)

        toolkit.print(
            f"Adding [cyan]{engine_info['name']}[/cyan] support...",
            tag="database",
        )
        toolkit.print_line()

        # Update config.py
        config_path = project_root / "app" / "core" / "config.py"
        if config_path.exists():
            toolkit.print("Updating config.py...", tag="config")
            if update_config_engine(config_path, engine):
                toolkit.print(f"  [green]✓[/green] Set DATABASE_ENGINE = '{engine}'")
            else:
                toolkit.print(f"  [yellow]⚠[/yellow] Could not update DATABASE_ENGINE")

        # Update .env file
        env_path = project_root / ".env"
        toolkit.print("Updating .env...", tag="env")
        if update_env_file(env_path, engine, engine_info["url_example"]):
            toolkit.print(f"  [green]✓[/green] Updated DATABASE_ENGINE in .env")
        else:
            toolkit.print(f"  [yellow]⚠[/yellow] Could not update .env")

        toolkit.print_line()

        # Install dependencies if requested
        if install:
            import subprocess
            import shutil

            toolkit.print("Installing dependencies...", tag="deps")

            if shutil.which("uv") is None:
                toolkit.print(
                    "[bold red]Error:[/bold red] uv is required to install dependencies.",
                    tag="error",
                )
                raise typer.Exit(code=1)

            for dep in engine_info["dependencies"]:
                try:
                    result = subprocess.run(
                        ["uv", "add", dep],
                        capture_output=True,
                        text=True,
                        cwd=project_root,
                    )
                    if result.returncode == 0:
                        toolkit.print(f"  [green]✓[/green] Installed {dep}")
                    else:
                        toolkit.print(f"  [yellow]⚠[/yellow] Failed to install {dep}")
                except Exception as e:
                    toolkit.print(f"  [red]✗[/red] Error installing {dep}: {e}")

            toolkit.print_line()

        # Success message
        toolkit.print(
            f"[bold green]✨ Success![/bold green] Added {engine_info['name']} support",
            tag="success",
        )

        toolkit.print_line()

        # Next steps
        toolkit.print("[bold]Configuration:[/bold]")
        toolkit.print(f"  DATABASE_ENGINE = '{engine}'")
        toolkit.print(f"  DATABASE_URL = '{engine_info['url_example']}'")

        toolkit.print_line()

        if not install:
            toolkit.print("[bold]Install dependencies:[/bold]")
            deps_str = " ".join(engine_info["dependencies"])
            toolkit.print(f"  [dim]$[/dim] uv add {deps_str}")
            toolkit.print_line()

        toolkit.print("[bold]Update your .env file:[/bold]")
        toolkit.print(f"  DATABASE_URL={engine_info['url_example']}")
