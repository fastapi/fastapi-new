import typer

from fastapi_new.new import new as new_command

app = typer.Typer(rich_markup_mode="rich")

app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)(new_command)


def main() -> None:
    app()
