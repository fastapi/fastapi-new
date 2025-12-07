from fastapi_new.core.config import ProjectConfig
from fastapi_new.constants.template import *
from rich_toolkit import RichToolkit
from textwrap import dedent
import pathlib
import subprocess
import typer


def generate_readme(project_name: str) -> str:
    return dedent(f"""
    # {project_name}
    
    A project created with FastAPI CLI (Custom Wizard).
    
    ## 📂 Structure

    - **app/controllers**: Routes & Endpoints logic
    - **app/models**: Database models (Pydantic/SQLModel)
    - **app/schemas**: Data validation schemas
    - **database**: Migrations & Seeders
    - **tests**: Unit & Integration tests
    
    ## 🚀 Quick Start

    1. Activate environment:
       - Windows: `.venv\\Scripts\\activate`
       - Mac/Linux: `source .venv/bin/activate`
    2. Run server:
       `uv run fastapi dev`
    """).strip()


def exit_with_error(toolkit: RichToolkit, error_msg: str) -> None:
    """
    Exit the program with an error message.

    Args:
        toolkit (RichToolkit): The RichToolkit instance for printing messages.
        error_msg (str): The error message to display.

    Returns:
        None
    """
    toolkit.print(f"[bold red]Error:[/bold red] {error_msg}", tag="error")
    raise typer.Exit(code=1)


def validate_python_version(python: str | None) -> str | None:
    """
    Validate the specified Python version.

    Args:
        python (str|None): The Python version string.

    Returns:
        str|None: An error message if the version is unsupported, otherwise None.
    """
    if not python:
        return None
    try:
        parts = python.split(".")
        if len(parts) < 2:
            return None
        major, minor = int(parts[0]), int(parts[1])
        if major < 3 or (major == 3 and minor < 10):
            return f"Python {python} is not supported. FastAPI requires Python 3.10+."
    except (ValueError, IndexError):
        pass
    return None


def setup_environment(toolkit: RichToolkit, config: ProjectConfig) -> None:
    """
    Set up the project environment using 'uv'.

    Args:
        toolkit (RichToolkit): The RichToolkit instance for printing messages.
        config (ProjectConfig): The project configuration.

    Returns:
        None
    """
    error = validate_python_version(config.python)
    if error:
        exit_with_error(toolkit, error)

    msg = "Setting up environment with uv"
    if config.python:
        msg += f" (Python {config.python})"
    toolkit.print(msg, tag="env")

    init_cmd = ["uv", "init", "--bare", "--no-workspace"]
    if not config.path.exists():
        config.path.mkdir(parents=True, exist_ok=True)

    if config.python:
        init_cmd.extend(["--python", config.python])

    try:
        subprocess.run(init_cmd, check=True, capture_output=True, cwd=config.path)
    except subprocess.CalledProcessError as e:
        exit_with_error(toolkit, f"Failed to init uv: {e.stderr.decode() if e.stderr else str(e)}")


def install_dependencies(toolkit: RichToolkit, config: ProjectConfig) -> None:
    """
    Install project dependencies and generate requirements.txt.

    Args:
        toolkit (RichToolkit): The RichToolkit instance for printing messages.
        config (ProjectConfig): The project configuration.

    Returns:
        None
    """
    toolkit.print("Installing dependencies & generating requirements.txt...", tag="deps")
    try:
        deps = ["fastapi[standard]", "python-dotenv"]

        if config.orm == "sqlmodel":
            deps.append("sqlmodel")
        elif config.orm == "sqlalchemy":
            deps.append("sqlalchemy")

        if config.views:
            deps.append("jinja2")

        if config.tests:
            deps.append("pytest")
            deps.append("httpx")

        if config.linter == "ruff":
            deps.append("ruff")
        elif config.linter == "classic":
            deps.extend(["black", "isort", "flake8"])

        subprocess.run(["uv", "add"] + deps, check=True, capture_output=True, cwd=config.path)

        with open(config.path / "requirements.txt", "w") as req_file:
            subprocess.run(
                ["uv", "export", "--format", "requirements-txt", "--no-hashes", "--no-header", "--no-annotate"],
                stdout=req_file,
                check=True,
                cwd=config.path
            )

    except subprocess.CalledProcessError as e:
        exit_with_error(toolkit, f"Failed to install deps: {e.stderr.decode() if e.stderr else str(e)}")


def create_file(path: pathlib.Path, content: str = "") -> None:
    """
    Create a file with the given content.

    Args:
        path (pathlib.Path): The file path to create.
        content (str): The content to write to the file.

    Returns:
        None
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_project_files(toolkit: RichToolkit, config: ProjectConfig) -> None:
    """
    Write the project files based on the configuration.
    Refactored for readability using helper functions.

    Args:
        toolkit (RichToolkit): The RichToolkit instance for printing messages.
        config (ProjectConfig): The project configuration.

    Returns:
        None
    """
    toolkit.print("Scaffolding project structure...", tag="template")
    try:
        _create_base_files(config)
        _setup_git(config)

        if config.views:
            _create_view_files(config)

        if config.orm != "none":
            _configure_database(config)

        if config.structure == "advanced":
            _setup_advanced_structure(config)

        hello_file = config.path / "hello.py"
        if hello_file.exists():
            hello_file.unlink()

    except Exception as e:
        exit_with_error(toolkit, f"Failed to write files: {str(e)}")


def _create_base_files(config: ProjectConfig) -> None:
    """Create the fundamental files for the project."""
    create_file(config.path / "main.py", TEMPLATE_MAIN)
    create_file(config.path / "README.md", generate_readme(config.name))


def _setup_git(config: ProjectConfig) -> None:
    """Create or update .gitignore."""
    gitignore_path = config.path / ".gitignore"
    
    if gitignore_path.exists():
        with open(gitignore_path, "a") as f:
            f.write("\n" + TEMPLATE_GITIGNORE)
    else:
        create_file(gitignore_path, TEMPLATE_GITIGNORE)


def _create_view_files(config: ProjectConfig) -> None:
    """Create HTML, CSS, and JS files."""
    base_view_path = config.path / "views"
    create_file(base_view_path / "html" / "index.html", TEMPLATE_HTML)
    create_file(base_view_path / "css" / "style.css", TEMPLATE_CSS)
    create_file(base_view_path / "js" / "main.js", TEMPLATE_JS)
    create_file(base_view_path / "assets" / ".gitkeep", "")


def _configure_database(config: ProjectConfig) -> None:
    """Setup database connection, env file, and gitignore."""
    # Create database config
    create_file(config.path / "config" / "database.py", TEMPLATE_DB_CONNECTION)

    # Create .env
    env_content = TEMPLATE_ENV.format(project_name=config.name)
    create_file(config.path / ".env", env_content.strip())


def _setup_advanced_structure(config: ProjectConfig) -> None:
    """Setup MVC folders, Migrations, Tests, and Linter config."""
    # 1. App Structure (MVC)
    mvc_paths = ["app", "app/controllers", "app/models", "app/schemas"]

    for p in mvc_paths:
        create_file(config.path / p / "__init__.py")

    # 2. Database Migrations
    create_file(config.path / "database" / "migrations" / ".gitkeep")
    create_file(config.path / "database" / "seeders" / ".gitkeep")

    # 3. Testing
    if config.tests:
        create_file(config.path / "tests" / "__init__.py")
        create_file(config.path / "tests" / "test_main.py", TEMPLATE_TESTING)

    # 4. Linter
    if config.linter == "ruff":
        create_file(config.path / ".ruff.toml", TEMPLATE_RUFF)