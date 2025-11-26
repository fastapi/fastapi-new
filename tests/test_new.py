"""
Tests for new project command.
"""

import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from fastapi_new.cli import app

runner = CliRunner()


@pytest.fixture
def temp_project_dir(tmp_path: Path, monkeypatch: Any) -> Path:
    """Create a temporary directory and cd into it."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


def _assert_project_structure_created(project_path: Path) -> None:
    """Assert that the full project structure was created."""
    # Check main directories
    assert (project_path / "app").exists()
    assert (project_path / "app" / "core").exists()
    assert (project_path / "app" / "apps").exists()
    assert (project_path / "app" / "db").exists()
    assert (project_path / "app" / "shared").exists()

    # Check core files
    assert (project_path / "app" / "main.py").exists()
    assert (project_path / "app" / "core" / "config.py").exists()
    assert (project_path / "app" / "core" / "registry.py").exists()
    assert (project_path / "app" / "core" / "database.py").exists()

    # Check db files
    assert (project_path / "app" / "db" / "base.py").exists()
    assert (project_path / "app" / "db" / "session.py").exists()

    # Check shared files
    assert (project_path / "app" / "shared" / "exceptions.py").exists()

    # Check root files
    assert (project_path / "pyproject.toml").exists()
    assert (project_path / "README.md").exists()
    assert (project_path / ".env").exists()


def _assert_minimal_files_created(project_path: Path) -> None:
    """Assert minimal required files exist (for backward compatibility tests)."""
    assert (project_path / "app" / "main.py").exists()
    assert (project_path / "README.md").exists()
    assert (project_path / "pyproject.toml").exists()


def test_creates_project_successfully(temp_project_dir: Path) -> None:
    """Test that a new project is created with full structure."""
    result = runner.invoke(app, ["my_fastapi_project"])

    assert result.exit_code == 0
    project_path = temp_project_dir / "my_fastapi_project"
    _assert_project_structure_created(project_path)
    assert "Success!" in result.output
    assert "my_fastapi_project" in result.output


def test_creates_project_with_python_version(temp_project_dir: Path) -> None:
    """Test creating project with specific Python version."""
    # Test long form
    result = runner.invoke(app, ["project_long", "--python", "3.12"])
    assert result.exit_code == 0
    project_path = temp_project_dir / "project_long"
    _assert_minimal_files_created(project_path)
    assert "3.12" in (project_path / "pyproject.toml").read_text()

    # Test short form
    result = runner.invoke(app, ["project_short", "-p", "3.11"])
    assert result.exit_code == 0
    project_path = temp_project_dir / "project_short"
    assert "3.11" in (project_path / "pyproject.toml").read_text()


def test_validates_main_py_contents(temp_project_dir: Path) -> None:
    """Test that main.py has correct content."""
    result = runner.invoke(app, ["sample_project"])
    assert result.exit_code == 0

    project_path = temp_project_dir / "sample_project"
    main_py_content = (project_path / "app" / "main.py").read_text()

    assert "from fastapi import FastAPI" in main_py_content
    assert "FastAPI" in main_py_content


def test_validates_config_py_contents(temp_project_dir: Path) -> None:
    """Test that config.py has correct content."""
    result = runner.invoke(app, ["config_project"])
    assert result.exit_code == 0

    project_path = temp_project_dir / "config_project"
    config_content = (project_path / "app" / "core" / "config.py").read_text()

    assert "Settings" in config_content
    assert "DATABASE" in config_content or "settings" in config_content


def test_validates_registry_py_contents(temp_project_dir: Path) -> None:
    """Test that registry.py has INSTALLED_APPS."""
    result = runner.invoke(app, ["registry_project"])
    assert result.exit_code == 0

    project_path = temp_project_dir / "registry_project"
    registry_content = (project_path / "app" / "core" / "registry.py").read_text()

    assert "INSTALLED_APPS" in registry_content


def test_validates_readme_contents(temp_project_dir: Path) -> None:
    """Test that README.md has project information."""
    result = runner.invoke(app, ["readme_project"])
    assert result.exit_code == 0

    project_path = temp_project_dir / "readme_project"
    readme_content = (project_path / "README.md").read_text()

    assert "readme_project" in readme_content or "FastAPI" in readme_content


def test_validates_env_file_created(temp_project_dir: Path) -> None:
    """Test that .env file is created with basic settings."""
    result = runner.invoke(app, ["env_project"])
    assert result.exit_code == 0

    project_path = temp_project_dir / "env_project"
    env_file = project_path / ".env"

    assert env_file.exists()
    env_content = env_file.read_text()
    assert "DATABASE" in env_content or "SECRET" in env_content


def test_validates_pyproject_contents(temp_project_dir: Path) -> None:
    """Test that pyproject.toml has correct dependencies."""
    result = runner.invoke(app, ["pyproject_test"])
    assert result.exit_code == 0

    project_path = temp_project_dir / "pyproject_test"
    pyproject_content = (project_path / "pyproject.toml").read_text()

    # Check for FastAPI dependency
    assert "fastapi" in pyproject_content.lower()


def test_initializes_in_current_directory(temp_project_dir: Path) -> None:
    """Test initializing project in current directory."""
    result = runner.invoke(app, [])

    assert result.exit_code == 0
    assert "No project name provided" in result.output
    assert "Initializing in current directory" in result.output
    _assert_minimal_files_created(temp_project_dir)


def test_rejects_existing_directory(temp_project_dir: Path) -> None:
    """Test that existing directory is rejected."""
    existing_dir = temp_project_dir / "existing_project"
    existing_dir.mkdir()

    result = runner.invoke(app, ["existing_project"])
    assert result.exit_code == 1
    assert "Directory 'existing_project' already exists" in result.output


def test_rejects_python_below_3_10(temp_project_dir: Path) -> None:
    """Test that Python versions below 3.10 are rejected."""
    result = runner.invoke(app, ["test_project", "--python", "3.9"])
    assert result.exit_code == 1
    assert "Python 3.9 is not supported" in result.output
    assert "FastAPI requires Python 3.10" in result.output


def test_rejects_python_2(temp_project_dir: Path) -> None:
    """Test that Python 2 is rejected."""
    result = runner.invoke(app, ["test_project", "--python", "2.7"])
    assert result.exit_code == 1
    assert "not supported" in result.output


def test_passes_single_digit_python_version_to_uv(temp_project_dir: Path) -> None:
    """Test that single digit Python version works."""
    result = runner.invoke(app, ["test_project", "--python", "3"])
    assert result.exit_code == 0
    project_path = temp_project_dir / "test_project"
    _assert_minimal_files_created(project_path)


def test_passes_malformed_python_version_to_uv(temp_project_dir: Path) -> None:
    """Test that malformed Python version is handled."""
    result = runner.invoke(app, ["test_project", "--python", "abc.def"])
    # uv will reject this, we just verify we don't crash during validation
    assert result.exit_code == 1


def test_creates_project_without_python_flag(temp_project_dir: Path) -> None:
    """Test creating project without specifying Python version."""
    result = runner.invoke(app, ["test_project"])
    assert result.exit_code == 0
    project_path = temp_project_dir / "test_project"
    _assert_minimal_files_created(project_path)


# Removed test for db/engines directory - intentionally deleted in simplification


def test_creates_shared_module_files(temp_project_dir: Path) -> None:
    """Test that shared module files are created."""
    result = runner.invoke(app, ["shared_project"])
    assert result.exit_code == 0

    project_path = temp_project_dir / "shared_project"
    shared_dir = project_path / "app" / "shared"

    assert (shared_dir / "exceptions.py").exists()
    assert (shared_dir / "utils.py").exists()
    assert (shared_dir / "constants.py").exists()


def test_creates_tests_directory(temp_project_dir: Path) -> None:
    """Test that tests directory is created."""
    result = runner.invoke(app, ["tests_project"])
    assert result.exit_code == 0

    project_path = temp_project_dir / "tests_project"
    tests_dir = project_path / "app" / "tests"

    assert tests_dir.exists()


def test_creates_plugins_directory(temp_project_dir: Path) -> None:
    """Test that plugins directory is created."""
    result = runner.invoke(app, ["plugins_project"])
    assert result.exit_code == 0

    project_path = temp_project_dir / "plugins_project"
    plugins_dir = project_path / "app" / "plugins"

    assert plugins_dir.exists()


def test_shows_next_steps(temp_project_dir: Path) -> None:
    """Test that next steps are shown after project creation."""
    result = runner.invoke(app, ["steps_project"])
    assert result.exit_code == 0

    assert "Next steps" in result.output
    assert "fastapi dev" in result.output or "createapp" in result.output


def test_shows_project_structure(temp_project_dir: Path) -> None:
    """Test that project structure is shown after creation."""
    result = runner.invoke(app, ["structure_project"])
    assert result.exit_code == 0

    # Should show some structure indication
    assert "app/" in result.output or "core/" in result.output


def test_failed_to_initialize_with_uv(monkeypatch: Any, temp_project_dir: Path) -> None:
    """Test handling of uv init failure."""
    call_count = 0

    def mock_run(*args: Any, **kwargs: Any) -> Any:
        nonlocal call_count
        call_count += 1
        cmd = args[0] if args else kwargs.get("args", [])

        # Let the first check for 'uv' succeed, but fail on 'uv init'
        if cmd[0] == "uv" and cmd[1] == "init":
            raise subprocess.CalledProcessError(
                1, cmd, stderr=b"uv init failed for some reason"
            )
        # Return success for other calls
        return type("Result", (), {"returncode": 0, "stdout": b"", "stderr": b""})()

    monkeypatch.setattr(subprocess, "run", mock_run)

    result = runner.invoke(app, ["failing_project"])
    assert result.exit_code == 1
    assert "Failed to initialize project with uv" in result.output


def test_uv_not_installed(temp_project_dir: Path, monkeypatch: Any) -> None:
    """Test error when uv is not installed."""
    monkeypatch.setattr(shutil, "which", lambda _: None)

    result = runner.invoke(app, ["test_uv_missing_project"])
    assert result.exit_code == 1
    assert "uv is required to create new projects" in result.output
    assert "https://docs.astral.sh/uv/" in result.output


def test_creates_gitignore(temp_project_dir: Path) -> None:
    """Test that .gitignore is created."""
    result = runner.invoke(app, ["gitignore_project"])
    assert result.exit_code == 0

    project_path = temp_project_dir / "gitignore_project"
    gitignore = project_path / ".gitignore"

    assert gitignore.exists()
    content = gitignore.read_text()
    assert "__pycache__" in content
    assert ".env" in content


def test_project_name_used_in_templates(temp_project_dir: Path) -> None:
    """Test that project name is correctly used in templates."""
    result = runner.invoke(app, ["awesome_api"])
    assert result.exit_code == 0

    project_path = temp_project_dir / "awesome_api"

    # Check config.py for project name
    config_content = (project_path / "app" / "core" / "config.py").read_text()
    assert "awesome_api" in config_content or "PROJECT_NAME" in config_content


def test_security_module_created(temp_project_dir: Path) -> None:
    """Test that security module is created."""
    result = runner.invoke(app, ["security_project"])
    assert result.exit_code == 0

    project_path = temp_project_dir / "security_project"
    security_file = project_path / "app" / "core" / "security.py"

    assert security_file.exists()
    content = security_file.read_text()
    assert "jwt" in content.lower() or "token" in content.lower() or "password" in content.lower()


# Removed test for container.py - intentionally deleted in simplification


class TestProjectDependencies:
    """Tests for project dependencies."""

    def test_includes_fastapi_dependency(self, temp_project_dir: Path) -> None:
        """Test that FastAPI is in dependencies."""
        result = runner.invoke(app, ["deps_project"])
        assert result.exit_code == 0

        project_path = temp_project_dir / "deps_project"
        pyproject_content = (project_path / "pyproject.toml").read_text()

        assert "fastapi" in pyproject_content.lower()

    def test_includes_sqlalchemy_dependency(self, temp_project_dir: Path) -> None:
        """Test that SQLAlchemy is in dependencies."""
        result = runner.invoke(app, ["sqlalchemy_project"])
        assert result.exit_code == 0

        project_path = temp_project_dir / "sqlalchemy_project"
        pyproject_content = (project_path / "pyproject.toml").read_text()

        assert "sqlalchemy" in pyproject_content.lower()

    def test_includes_pydantic_settings(self, temp_project_dir: Path) -> None:
        """Test that pydantic-settings is in dependencies."""
        result = runner.invoke(app, ["pydantic_project"])
        assert result.exit_code == 0

        project_path = temp_project_dir / "pydantic_project"
        pyproject_content = (project_path / "pyproject.toml").read_text()

        assert "pydantic" in pyproject_content.lower()
