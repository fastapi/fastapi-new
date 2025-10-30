import typer

from fastapi_new.new import new as new_command

app = typer.Typer(rich_markup_mode="rich")

app.command()(new_command)


def main() -> None:
    app()
