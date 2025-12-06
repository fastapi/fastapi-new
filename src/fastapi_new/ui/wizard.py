from fastapi_new.core.config import ProjectConfig
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm

def run_interactive_wizard() -> ProjectConfig:
    console = Console()
    
    name = Prompt.ask("📂 What is your [bold green]Project Name[/]")
    path = Path.cwd() / name

    console.print("\n[bold]🏗️  Architecture[/]")
    console.print("   [bold cyan]1.[/] Simple   [dim](Flat structure, microservices)[/]")
    console.print("   [bold cyan]2.[/] Advanced [dim](Laravel-style MVC, scalable)[/]")
    
    struct_choice = Prompt.ask(
        "Choose style",
        choices=["1", "2"], 
        show_choices=False,
        default="1"
    )

    structure = "advanced" if struct_choice == "2" else "simple"

    console.print("\n[bold]💽 Database / ORM[/]")
    console.print("   [bold cyan]1.[/] SQLModel   [dim](Recommended for FastAPI)[/]")
    console.print("   [bold cyan]2.[/] SQLAlchemy [dim](Classic & Robust)[/]")
    console.print("   [bold cyan]3.[/] None       [dim](No database)[/]")
    
    orm_choice = Prompt.ask(
        "Select ORM", 
        choices=["1", "2", "3"],
        show_choices=False,
        default="1"
    )
    
    orm_map = {"1": "sqlmodel", "2": "sqlalchemy", "3": "none"}
    orm = orm_map[orm_choice]

    console.print("\n[bold]🎨 Frontend / Views[/]")
    include_views = Confirm.ask("Add Views (HTML/CSS/JS)?", default=False)

    console.print("\n[bold]🧪 Quality Assurance[/]")
    include_tests = Confirm.ask("Add Testing (Pytest)?", default=True)

    return ProjectConfig(
        name=name,
        path=path,
        structure=structure,
        orm=orm,
        views=include_views,
        tests=include_tests
    )