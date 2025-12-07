from .core.generator import *
from .ui.styles import get_rich_toolkit
from .ui.wizard import run_interactive_wizard
from typing import Annotated
import shutil
import typer


def new(
    project_name: Annotated[str | None, typer.Argument()] = None,
    python: Annotated[str | None, typer.Option()] = None,
) -> None:
    with get_rich_toolkit() as toolkit:
        if shutil.which("uv") is None:
            exit_with_error(toolkit, "uv is required. Please install uv first.")

        config = run_interactive_wizard(default_name=project_name)

        if python:
            config.python = python

        toolkit.print_title("Creating a new project 🚀", tag="FastAPI")

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