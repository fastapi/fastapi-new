from fastapi_new.core.config import ProjectConfig
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
from typer import Exit


def run_interactive_wizard(default_name: str | None = None) -> ProjectConfig:
    console = Console()

    # Project Name
    if default_name:
        name = default_name
        console.print(f"📂 Project Name: [bold green]{name}[/]")
    else:
        name = Prompt.ask("📂 What is your [bold green]Project Name[/]")

    path = Path.cwd() / name

    if path.exists():
        console.print(
            f"[bold red]Error:[/bold red] Directory '{name}' already exists.")
        raise Exit(code=1)

    # Architecture
    console.print("\n[bold]🏗️  Architecture[/]")
    console.print("   [bold cyan]1.[/] Simple   [dim](Flat structure, microservices)[/]")
    console.print("   [bold cyan]2.[/] Advanced [dim](MVC structure, scalable)[/]")
    struct_choice = Prompt.ask("Choose style", choices=["1", "2"], show_choices=False, default="1")
    structure = "advanced" if struct_choice == "2" else "simple"

    # Database
    console.print("\n[bold]💽 Database / ORM[/]")
    console.print("   [bold cyan]1.[/] SQLModel   [dim](Recommended for FastAPI)[/]")
    console.print("   [bold cyan]2.[/] SQLAlchemy [dim](Classic & Robust)[/]")
    console.print("   [bold cyan]3.[/] None       [dim](No database)[/]")
    orm_choice = Prompt.ask("Select ORM", choices=["1", "2", "3"], show_choices=False, default="1")
    orm_map = {"1": "sqlmodel", "2": "sqlalchemy", "3": "none"}
    orm = orm_map[orm_choice]

    # Linting
    console.print("\n[bold]✨ Linting & Formatting[/]")
    console.print("   [bold cyan]1.[/] Ruff       [dim](Recommended - Blazing fast)[/]")
    console.print("   [bold cyan]2.[/] Classic    [dim](Black + Isort + Flake8)[/]")
    console.print("   [bold cyan]3.[/] None       [dim](Skip linting)[/]")
    lint_choice = Prompt.ask("Select Linter", choices=["1", "2", "3"], show_choices=False, default="1")
    linter_map = {"1": "ruff", "2": "classic", "3": "none"}
    linter = linter_map[lint_choice]

    # Views
    console.print("\n[bold]🎨 Frontend / Views[/]")
    include_views = Confirm.ask("Add Views (HTML/CSS/JS)?", default=False)

    # Testing
    console.print("\n[bold]🧪 Quality Assurance[/]")
    include_tests = Confirm.ask("Add Testing (Pytest)?", default=True)

    return ProjectConfig(
        linter=linter,
        name=name,
        orm=orm,
        path=path,
        structure=structure,
        tests=include_tests,
        views=include_views,
    )