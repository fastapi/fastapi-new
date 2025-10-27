import pathlib
import shutil
import subprocess
from dataclasses import dataclass, field
from typing import Annotated

import typer
from rich_toolkit import RichToolkit

from .utils.cli import get_rich_toolkit

# TODO: Add ability to fetch different templates in the future via --template option
TEMPLATE_CONTENT = """from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def main():
    return {"message": "Hello World"}
"""


@dataclass
class ProjectConfig:
    name: str
    path: pathlib.Path
    extra_args: list[str] = field(default_factory=list)


def _generate_readme(project_name: str) -> str:
    return f"""# {project_name}

A project created with FastAPI Cloud CLI.

## Quick Start

Start the development server:

```bash
uv run fastapi dev
```

Visit http://localhost:8000

Deploy to FastAPI Cloud:

```bash
uv run fastapi login
uv run fastapi deploy
```

## Project Structure

- `main.py` - Your FastAPI application
- `pyproject.toml` - Project dependencies

## Learn More

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [FastAPI Cloud](https://fastapicloud.com)
"""


def _exit_with_error(toolkit: RichToolkit, error_msg: str) -> None:
    toolkit.print(f"[bold red]Error:[/bold red] {error_msg}", tag="error")
    raise typer.Exit(code=1)


def _validate_python_version_in_args(extra_args: list[str]) -> str | None:
    """
    Check if --python is specified in extra_args and validate it's >= 3.8.
    Returns error message if < 3.8, None otherwise.
    Let uv handle malformed versions or versions it can't find.
    """
    if not extra_args:
        return None

    for i, arg in enumerate(extra_args):
        if arg in ("--python", "-p") and i + 1 < len(extra_args):
            version_str = extra_args[i + 1]
            try:
                parts = version_str.split(".")
                if len(parts) < 2:
                    return None  # Let uv handle malformed version
                major, minor = int(parts[0]), int(parts[1])

                if major < 3 or (major == 3 and minor < 8):
                    return f"Python {version_str} is not supported. FastAPI requires Python 3.8 or higher."
                return None
            except (ValueError, IndexError):
                # Malformed version - let uv handle the error
                return None
    return None


def _setup(toolkit: RichToolkit, config: ProjectConfig) -> None:
    error = _validate_python_version_in_args(config.extra_args)
    if error:
        _exit_with_error(toolkit, error)

    msg = "Setting up environment with uv"

    if config.extra_args:
        msg += f" ({' '.join(config.extra_args)})"

    toolkit.print(msg, tag="env")

    # If config.name is provided, create in subdirectory; otherwise init in current dir
    # uv will infer the project name from the directory name
    if config.path == pathlib.Path.cwd():
        init_cmd = ["uv", "init"]
    else:
        init_cmd = ["uv", "init", config.name]

    if config.extra_args:
        init_cmd.extend(config.extra_args)

    try:
        subprocess.run(init_cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.decode() if e.stderr else "No details available"
        _exit_with_error(toolkit, f"Failed to initialize project with uv. {stderr}")


def _install_dependencies(toolkit: RichToolkit, config: ProjectConfig) -> None:
    toolkit.print("Installing dependencies...", tag="deps")

    try:
        subprocess.run(
            ["uv", "add", "fastapi[standard]"],
            check=True,
            capture_output=True,
            cwd=config.path,
        )
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.decode() if e.stderr else "No details available"
        _exit_with_error(toolkit, f"Failed to install dependencies. {stderr}")


def _write_template_files(toolkit: RichToolkit, config: ProjectConfig) -> None:
    toolkit.print("Writing template files...", tag="template")
    readme_content = _generate_readme(config.name)

    try:
        (config.path / "main.py").write_text(TEMPLATE_CONTENT)
        (config.path / "README.md").write_text(readme_content)
    except Exception as e:
        _exit_with_error(toolkit, f"Failed to write template files. {str(e)}")


def new(
    ctx: typer.Context,
    project_name: Annotated[
        str | None,
        typer.Argument(
            help="The name of the new FastAPI Cloud project. If not provided, initializes in the current directory.",
        ),
    ] = None,
) -> None:
    if project_name:
        name = project_name
        path = pathlib.Path.cwd() / project_name
    else:
        name = pathlib.Path.cwd().name
        path = pathlib.Path.cwd()

    config = ProjectConfig(
        name=name,
        path=path,
        extra_args=ctx.args if hasattr(ctx, "args") else [],
    )

    with get_rich_toolkit() as toolkit:
        toolkit.print_title("Creating a new project 🚀", tag="FastAPI")

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

        if shutil.which("uv") is None:
            _exit_with_error(
                toolkit,
                "uv is required to create new projects. Install it from https://docs.astral.sh/uv/getting-started/installation/",
            )

        _setup(toolkit, config)

        toolkit.print_line()

        _install_dependencies(toolkit, config)

        toolkit.print_line()

        _write_template_files(toolkit, config)

        toolkit.print_line()

        # Print success message
        if project_name:
            toolkit.print(
                f"[bold green]✨ Success![/bold green] Created FastAPI project: [cyan]{project_name}[/cyan]",
                tag="success",
            )

            toolkit.print_line()

            toolkit.print("[bold]Next steps:[/bold]")
            toolkit.print(f"  [dim]$[/dim] cd {project_name}")
            toolkit.print("  [dim]$[/dim] uv run fastapi dev")
        else:
            toolkit.print(
                "[bold green]✨ Success![/bold green] Initialized FastAPI project in current directory",
                tag="success",
            )

            toolkit.print_line()

            toolkit.print("[bold]Next steps:[/bold]")
            toolkit.print("  [dim]$[/dim] uv run fastapi dev")

        toolkit.print_line()

        toolkit.print("Visit [blue]http://localhost:8000[/blue]")

        toolkit.print_line()

        toolkit.print("[bold]Deploy to FastAPI Cloud:[/bold]")
        toolkit.print("  [dim]$[/dim] uv run fastapi login")
        toolkit.print("  [dim]$[/dim] uv run fastapi deploy")

        toolkit.print_line()

        toolkit.print(
            "[dim]💡 Tip: Use 'uv run' to automatically use the project's environment[/dim]"
        )
