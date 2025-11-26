"""
FastAPI-New CLI
Main command-line interface for FastAPI-New framework.
"""

from typing import Any

import click
from typer.core import TyperGroup

import typer

from fastapi_new.new import new as new_command
from fastapi_new.createapp import createapp as createapp_command
from fastapi_new.adddb import adddb as adddb_command
from fastapi_new.listapps import listapps as listapps_command
from fastapi_new.doctor import doctor as doctor_command


class DefaultCommandGroup(TyperGroup):
    """
    Custom TyperGroup that routes unknown commands to a default command.

    This enables the pattern:
        fastapi-new myproject           -> routes to 'new myproject'
        fastapi-new                     -> routes to 'new' (no args)
        fastapi-new new myproject       -> explicit 'new' subcommand
        fastapi-new createapp users     -> normal subcommand
    """

    def __init__(self, *args: Any, default_cmd: str = "new", **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.default_cmd = default_cmd

    def parse_args(self, ctx: click.Context, args: list[str]) -> list[str]:
        """Override argument parsing to handle default command routing."""
        # If no arguments, invoke the default command
        if not args:
            args = [self.default_cmd]
        # If first arg is not a known command/option, prepend the default command
        elif args[0] not in self.commands and not args[0].startswith("-"):
            args = [self.default_cmd] + args

        return super().parse_args(ctx, args)

    def resolve_command(
        self, ctx: click.Context, args: list[str]
    ) -> tuple[str | None, click.Command | None, list[str]]:
        """Resolve command, routing to default if needed."""
        return super().resolve_command(ctx, args)


# Create the main Typer app with our custom Click group
app = typer.Typer(
    name="fastapi-new",
    help="FastAPI-New: A modular enterprise framework for FastAPI",
    rich_markup_mode="rich",
    cls=DefaultCommandGroup,
    no_args_is_help=False,
)


# Register the 'new' command (this is also the default)
app.command(name="new", help="Create a new FastAPI-New project")(new_command)

# Register subcommands for project management
app.command(name="createapp", help="Create a new MSSR app module")(createapp_command)
app.command(name="add-db", help="Add database engine support")(adddb_command)
app.command(name="list", help="List installed app modules")(listapps_command)
app.command(name="doctor", help="Diagnose project structure")(doctor_command)


def main() -> None:
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
