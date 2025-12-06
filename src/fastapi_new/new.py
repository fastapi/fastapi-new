from .core.generator import setup_environment, install_dependencies, write_project_files, exit_with_error
from .ui.styles import get_rich_toolkit
from .ui.wizard import run_interactive_wizard
from fastapi_new.core.config import ProjectConfig
from pathlib import Path
from shutil import which
from typer import Argument, Context, Option
from typing import Annotated


def new(
    ctx: Context,
    project_name: Annotated[str | None, Argument()] = None,
    python: Annotated[str | None, Option()] = None,
) -> None:
    if project_name:
        path = Path.cwd() / project_name
        config = ProjectConfig(name=project_name, path=path, python=python)
    else:
        config = run_interactive_wizard()
        if python:
            config.python = python

    with get_rich_toolkit() as toolkit:
        toolkit.print_title("Creating a new project 🚀", tag="FastAPI")

        if config.path.exists():
            exit_with_error(toolkit, f"Directory '{config.name}' already exists.")

        if which("uv") is None:
            exit_with_error(toolkit, "uv is required. Please install uv first.")

        setup_environment(toolkit, config)
        install_dependencies(toolkit, config)
        write_project_files(toolkit, config)

        toolkit.print_line()
        toolkit.print(
            f"[bold green]✨ Success![/bold green] Created project: [cyan]{config.name}[/cyan]",
            tag="success",
        )

        toolkit.print(f"  [dim]$[/dim] cd {config.name}")
        toolkit.print("  [dim]$[/dim] uv run fastapi dev")