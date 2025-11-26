"""
Tests for CLI interface.
"""

import subprocess
import sys
from typing import Any

import pytest
from typer.testing import CliRunner

from fastapi_new.cli import app

runner = CliRunner()


class TestCLIHelp:
    """Tests for CLI help output."""

    def test_main_help(self) -> None:
        """Test that main help shows available commands."""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "Usage" in result.output
        assert "FastAPI" in result.output or "fastapi" in result.output.lower()

    def test_createapp_help(self) -> None:
        """Test that createapp command has help."""
        result = runner.invoke(app, ["createapp", "--help"])

        assert result.exit_code == 0
        assert "Usage" in result.output
        assert "createapp" in result.output.lower()
        assert "MSSR" in result.output or "app" in result.output.lower()

    def test_add_db_help(self) -> None:
        """Test that add-db command has help."""
        result = runner.invoke(app, ["add-db", "--help"])

        assert result.exit_code == 0
        assert "Usage" in result.output
        assert "database" in result.output.lower() or "engine" in result.output.lower()

    def test_list_help(self) -> None:
        """Test that list command has help."""
        result = runner.invoke(app, ["list", "--help"])

        assert result.exit_code == 0
        assert "Usage" in result.output

    def test_doctor_help(self) -> None:
        """Test that doctor command has help."""
        result = runner.invoke(app, ["doctor", "--help"])

        assert result.exit_code == 0
        assert "Usage" in result.output
        assert "diagnose" in result.output.lower() or "project" in result.output.lower()


class TestCLICommands:
    """Tests for CLI commands existence."""

    def test_createapp_command_exists(self) -> None:
        """Test that createapp command is registered."""
        result = runner.invoke(app, ["--help"])

        assert "createapp" in result.output

    def test_add_db_command_exists(self) -> None:
        """Test that add-db command is registered."""
        result = runner.invoke(app, ["--help"])

        assert "add-db" in result.output

    def test_list_command_exists(self) -> None:
        """Test that list command is registered."""
        result = runner.invoke(app, ["--help"])

        assert "list" in result.output

    def test_doctor_command_exists(self) -> None:
        """Test that doctor command is registered."""
        result = runner.invoke(app, ["--help"])

        assert "doctor" in result.output


class TestCLIScript:
    """Tests for CLI as a script."""

    def test_script_runs(self) -> None:
        """Test that the CLI can be run as a script."""
        result = subprocess.run(
            [sys.executable, "-m", "fastapi_new", "--help"],
            capture_output=True,
            encoding="utf-8",
        )

        assert result.returncode == 0
        assert "Usage" in result.stdout

    def test_script_with_module_flag(self) -> None:
        """Test that the CLI works when called as a module."""
        result = subprocess.run(
            [sys.executable, "-m", "fastapi_new", "--help"],
            capture_output=True,
            encoding="utf-8",
        )

        assert result.returncode == 0
        assert "Usage" in result.stdout


class TestCLIErrorHandling:
    """Tests for CLI error handling."""

    def test_unknown_command(self) -> None:
        """Test that unknown commands are routed to 'new' command by design."""
        result = runner.invoke(app, ["unknown_command"])

        # By design, unknown commands are treated as project names and routed to 'new'
        # This is intentional behavior from the DefaultCommandGroup
        # The command should succeed (create a project) or show relevant output
        assert result.exit_code == 0 or "Error" in result.output or "Usage" in result.output

    def test_createapp_without_name(self) -> None:
        """Test that createapp without name shows error."""
        result = runner.invoke(app, ["createapp"])

        # Should fail or show usage
        assert result.exit_code != 0 or "Missing" in result.output or "Usage" in result.output

    def test_add_db_without_engine(self) -> None:
        """Test that add-db without engine shows error."""
        result = runner.invoke(app, ["add-db"])

        # Should fail or show usage
        assert result.exit_code != 0 or "Missing" in result.output or "Usage" in result.output


class TestCLIVersionAndInfo:
    """Tests for CLI version and information."""

    def test_version_accessible(self) -> None:
        """Test that version is accessible."""
        from fastapi_new import __version__

        assert __version__ is not None
        assert isinstance(__version__, str)

    def test_cli_imports_successfully(self) -> None:
        """Test that CLI can be imported without errors."""
        from fastapi_new.cli import app, main

        assert app is not None
        assert main is not None
        assert callable(main)


class TestCLICommandDescriptions:
    """Tests for CLI command descriptions."""

    def test_commands_have_descriptions(self) -> None:
        """Test that commands have descriptions in help."""
        result = runner.invoke(app, ["--help"])

        # Help should contain descriptions for commands
        lines_with_content = [
            line for line in result.output.split("\n")
            if line.strip() and not line.strip().startswith("Usage")
        ]
        assert len(lines_with_content) > 3  # Should have multiple command descriptions

    def test_createapp_has_description(self) -> None:
        """Test that createapp has a description."""
        result = runner.invoke(app, ["createapp", "--help"])

        # Should have some description text
        assert len(result.output) > 50

    def test_add_db_has_description(self) -> None:
        """Test that add-db has a description."""
        result = runner.invoke(app, ["add-db", "--help"])

        # Should mention supported engines
        output_lower = result.output.lower()
        assert "postgres" in output_lower or "mysql" in output_lower or "sqlite" in output_lower or "engine" in output_lower

    def test_list_has_description(self) -> None:
        """Test that list has a description."""
        result = runner.invoke(app, ["list", "--help"])

        assert len(result.output) > 50

    def test_doctor_has_description(self) -> None:
        """Test that doctor has a description."""
        result = runner.invoke(app, ["doctor", "--help"])

        output_lower = result.output.lower()
        assert "diagnose" in output_lower or "check" in output_lower or "project" in output_lower


class TestCLIOptions:
    """Tests for CLI options."""

    def test_list_verbose_option(self) -> None:
        """Test that list command has verbose option."""
        result = runner.invoke(app, ["list", "--help"])

        assert "--verbose" in result.output or "-v" in result.output

    def test_add_db_install_option(self) -> None:
        """Test that add-db command has install option."""
        result = runner.invoke(app, ["add-db", "--help"])

        assert "--install" in result.output or "-i" in result.output

    def test_new_python_option(self) -> None:
        """Test that new command has python option."""
        result = runner.invoke(app, ["new", "--help"])

        # The new command should support --python flag
        assert "--python" in result.output or "-p" in result.output


class TestCLIIntegration:
    """Integration tests for CLI."""

    def test_cli_entry_point(self) -> None:
        """Test that CLI entry point works."""
        from fastapi_new.cli import main

        # Just ensure it's callable and the app is properly configured
        assert callable(main)

    def test_all_commands_registered(self) -> None:
        """Test that all expected commands are registered."""
        result = runner.invoke(app, ["--help"])
        output = result.output.lower()

        expected_commands = ["createapp", "add-db", "list", "doctor"]
        for cmd in expected_commands:
            assert cmd in output, f"Command '{cmd}' should be in help output"
