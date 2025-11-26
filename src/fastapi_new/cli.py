"""
FastAPI-New CLI
Main command-line interface for FastAPI-New framework.
"""

import typer

from fastapi_new.new import new as new_command
from fastapi_new.createapp import createapp as createapp_command
from fastapi_new.adddb import adddb as adddb_command
from fastapi_new.listapps import listapps as listapps_command
from fastapi_new.doctor import doctor as doctor_command

app = typer.Typer(
    name="fastapi-new",
    help="FastAPI-New: A modular enterprise framework for FastAPI",
    rich_markup_mode="rich",
)

# Register commands
# The 'new' command is the default - creates a new project
app.command()(new_command)

# Subcommands for project management
app.command(name="createapp")(createapp_command)
app.command(name="add-db")(adddb_command)
app.command(name="list")(listapps_command)
app.command(name="doctor")(doctor_command)


def main() -> None:
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
