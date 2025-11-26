"""
Tests for doctor command.
"""

import pytest
from pathlib import Path
from typing import Any

from typer.testing import CliRunner

from fastapi_new.cli import app
from fastapi_new.doctor import (
    find_project_root,
    check_directories,
    check_files,
    check_installed_apps,
    check_env_file,
    check_main_py,
    REQUIRED_DIRS,
    REQUIRED_CORE_FILES,
    REQUIRED_DB_FILES,
)

runner = CliRunner()


@pytest.fixture
def minimal_project(tmp_path: Path) -> Path:
    """Create a minimal FastAPI-New project structure."""
    # Create required directories
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "core").mkdir()
    (tmp_path / "app" / "apps").mkdir()
    (tmp_path / "app" / "db").mkdir()
    (tmp_path / "app" / "shared").mkdir()

    return tmp_path


@pytest.fixture
def complete_project(minimal_project: Path) -> Path:
    """Create a complete FastAPI-New project structure."""
    # Create core files
    (minimal_project / "app" / "core" / "config.py").write_text('settings = {}')
    (minimal_project / "app" / "core" / "registry.py").write_text('''
INSTALLED_APPS: list[str] = [
    "users",
]
''')
    (minimal_project / "app" / "core" / "database.py").write_text('# Database')
    (minimal_project / "app" / "core" / "security.py").write_text('# Security')
    (minimal_project / "app" / "core" / "container.py").write_text('# Container')

    # Create db files
    (minimal_project / "app" / "db" / "base.py").write_text('# Base')
    (minimal_project / "app" / "db" / "session.py").write_text('# Session')

    # Create shared files
    (minimal_project / "app" / "shared" / "exceptions.py").write_text('# Exceptions')
    (minimal_project / "app" / "shared" / "utils.py").write_text('# Utils')
    (minimal_project / "app" / "shared" / "constants.py").write_text('# Constants')

    # Create main.py
    (minimal_project / "app" / "main.py").write_text('''
from fastapi import FastAPI
app = FastAPI()
''')

    # Create .env file
    (minimal_project / ".env").write_text('''
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=my-production-key
''')

    # Create users app
    users_dir = minimal_project / "app" / "apps" / "users"
    users_dir.mkdir()
    (users_dir / "__init__.py").write_text('')
    (users_dir / "routes.py").write_text('from fastapi import APIRouter\nrouter = APIRouter()')

    return minimal_project


@pytest.fixture
def temp_project_dir(complete_project: Path, monkeypatch: Any) -> Path:
    """Create a temporary project directory and cd into it."""
    monkeypatch.chdir(complete_project)
    return complete_project


class TestFindProjectRoot:
    """Tests for find_project_root function."""

    def test_finds_root_in_current_directory(self, tmp_path: Path, monkeypatch: Any) -> None:
        (tmp_path / "app").mkdir()
        monkeypatch.chdir(tmp_path)

        result = find_project_root()
        assert result == tmp_path

    def test_finds_root_in_parent_directory(self, tmp_path: Path, monkeypatch: Any) -> None:
        (tmp_path / "app").mkdir()
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        monkeypatch.chdir(subdir)

        result = find_project_root()
        assert result == tmp_path

    def test_finds_root_in_nested_directory(self, tmp_path: Path, monkeypatch: Any) -> None:
        (tmp_path / "app").mkdir()
        nested = tmp_path / "a" / "b"
        nested.mkdir(parents=True)
        monkeypatch.chdir(nested)

        result = find_project_root()
        assert result == tmp_path

    def test_returns_none_when_no_project(self, tmp_path: Path, monkeypatch: Any) -> None:
        monkeypatch.chdir(tmp_path)

        result = find_project_root()
        assert result is None


class TestCheckDirectories:
    """Tests for check_directories function."""

    def test_all_directories_exist(self, complete_project: Path) -> None:
        results = check_directories(complete_project)

        for path, exists, msg in results:
            assert exists is True, f"{path} should exist"
            assert msg == "OK"

    def test_missing_directories(self, tmp_path: Path) -> None:
        # Only create app directory
        (tmp_path / "app").mkdir()

        results = check_directories(tmp_path)

        # app should exist
        app_result = next((r for r in results if r[0] == "app"), None)
        assert app_result is not None
        assert app_result[1] is True

        # app/core should be missing
        core_result = next((r for r in results if r[0] == "app/core"), None)
        assert core_result is not None
        assert core_result[1] is False
        assert "Missing" in core_result[2]

    def test_checks_all_required_dirs(self, tmp_path: Path) -> None:
        (tmp_path / "app").mkdir()

        results = check_directories(tmp_path)

        # Should check all REQUIRED_DIRS
        checked_paths = [r[0] for r in results]
        for required_dir in REQUIRED_DIRS:
            assert required_dir in checked_paths


class TestCheckFiles:
    """Tests for check_files function."""

    def test_all_files_exist(self, complete_project: Path) -> None:
        results = check_files(complete_project, REQUIRED_CORE_FILES, required=True)

        for path, exists, msg in results:
            assert exists is True, f"{path} should exist"
            assert msg == "OK"

    def test_missing_required_files(self, minimal_project: Path) -> None:
        results = check_files(minimal_project, REQUIRED_CORE_FILES, required=True)

        for path, exists, msg in results:
            assert exists is False
            assert "required" in msg.lower()

    def test_missing_optional_files(self, minimal_project: Path) -> None:
        results = check_files(minimal_project, ["app/core/security.py"], required=False)

        for path, exists, msg in results:
            assert exists is False
            assert "optional" in msg.lower()


class TestCheckInstalledApps:
    """Tests for check_installed_apps function."""

    def test_valid_installed_apps(self, complete_project: Path) -> None:
        results = check_installed_apps(complete_project)

        # Should have users app which is valid
        users_result = next((r for r in results if r[0] == "users"), None)
        assert users_result is not None
        assert users_result[1] is True
        assert users_result[2] == "OK"

    def test_missing_app_directory(self, complete_project: Path) -> None:
        # Update registry to include non-existent app
        registry_path = complete_project / "app" / "core" / "registry.py"
        registry_path.write_text('''
INSTALLED_APPS: list[str] = [
    "users",
    "nonexistent",
]
''')

        results = check_installed_apps(complete_project)

        # nonexistent should be flagged
        nonexistent_result = next((r for r in results if r[0] == "nonexistent"), None)
        assert nonexistent_result is not None
        assert nonexistent_result[1] is False
        assert "not found" in nonexistent_result[2].lower()

    def test_missing_routes_py(self, complete_project: Path) -> None:
        # Update registry and create app without routes.py
        registry_path = complete_project / "app" / "core" / "registry.py"
        registry_path.write_text('''
INSTALLED_APPS: list[str] = [
    "products",
]
''')

        products_dir = complete_project / "app" / "apps" / "products"
        products_dir.mkdir()
        (products_dir / "__init__.py").write_text('')

        results = check_installed_apps(complete_project)

        products_result = next((r for r in results if r[0] == "products"), None)
        assert products_result is not None
        assert products_result[1] is False
        assert "routes" in products_result[2].lower()

    def test_empty_installed_apps(self, complete_project: Path) -> None:
        registry_path = complete_project / "app" / "core" / "registry.py"
        registry_path.write_text('''
INSTALLED_APPS: list[str] = [
]
''')

        results = check_installed_apps(complete_project)

        # Should indicate empty list
        assert len(results) == 1
        assert "Empty" in results[0][2] or "no apps" in results[0][2].lower()

    def test_missing_registry_file(self, minimal_project: Path) -> None:
        results = check_installed_apps(minimal_project)

        assert len(results) == 1
        assert results[0][1] is False
        assert "not found" in results[0][2].lower()


class TestCheckEnvFile:
    """Tests for check_env_file function."""

    def test_env_file_exists_with_all_vars(self, complete_project: Path) -> None:
        results = check_env_file(complete_project)

        env_result = next((r for r in results if r[0] == ".env"), None)
        assert env_result is not None
        assert env_result[1] is True

        db_result = next((r for r in results if r[0] == "DATABASE_URL"), None)
        assert db_result is not None
        assert db_result[1] is True

        secret_result = next((r for r in results if r[0] == "SECRET_KEY"), None)
        assert secret_result is not None
        assert secret_result[1] is True

    def test_env_file_missing(self, minimal_project: Path) -> None:
        results = check_env_file(minimal_project)

        env_result = next((r for r in results if r[0] == ".env"), None)
        assert env_result is not None
        assert env_result[1] is False

    def test_env_example_suggested_when_env_missing(self, minimal_project: Path) -> None:
        # Create .env.example
        (minimal_project / ".env.example").write_text("DATABASE_URL=")

        results = check_env_file(minimal_project)

        # Should suggest copying from .env.example
        example_result = next((r for r in results if ".env.example" in r[0]), None)
        assert example_result is not None
        assert example_result[1] is True
        assert "copy" in example_result[2].lower() or "Available" in example_result[2]

    def test_default_secret_key_warning(self, minimal_project: Path) -> None:
        (minimal_project / ".env").write_text('''
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=your-secret-key-change-in-production
''')

        results = check_env_file(minimal_project)

        secret_result = next((r for r in results if r[0] == "SECRET_KEY"), None)
        assert secret_result is not None
        assert secret_result[1] is False
        assert "default" in secret_result[2].lower() or "change" in secret_result[2].lower()

    def test_missing_database_url(self, minimal_project: Path) -> None:
        (minimal_project / ".env").write_text('''
SECRET_KEY=my-secret
''')

        results = check_env_file(minimal_project)

        db_result = next((r for r in results if r[0] == "DATABASE_URL"), None)
        assert db_result is not None
        assert db_result[1] is False


class TestCheckMainPy:
    """Tests for check_main_py function."""

    def test_valid_main_py(self, complete_project: Path) -> None:
        ok, msg = check_main_py(complete_project)

        assert ok is True
        assert msg == "OK"

    def test_missing_main_py(self, minimal_project: Path) -> None:
        ok, msg = check_main_py(minimal_project)

        assert ok is False
        assert "Not found" in msg

    def test_main_py_without_fastapi(self, minimal_project: Path) -> None:
        (minimal_project / "app" / "main.py").write_text('''
# No framework import here
print("Hello")
''')

        ok, msg = check_main_py(minimal_project)

        assert ok is False
        assert "FastAPI" in msg

    def test_main_py_without_app_instance(self, minimal_project: Path) -> None:
        (minimal_project / "app" / "main.py").write_text('''
from fastapi import FastAPI
# No app instance
''')

        ok, msg = check_main_py(minimal_project)

        assert ok is False
        assert "app" in msg.lower()


class TestDoctorCommand:
    """Tests for doctor CLI command."""

    def test_healthy_project(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["doctor"])

        assert result.exit_code == 0
        assert "passed" in result.output.lower() or "healthy" in result.output.lower()

    def test_shows_project_root(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["doctor"])

        assert result.exit_code == 0
        assert "Project root" in result.output or str(temp_project_dir) in result.output

    def test_checks_directories(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["doctor"])

        assert result.exit_code == 0
        assert "Directories" in result.output

    def test_checks_core_files(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["doctor"])

        assert result.exit_code == 0
        assert "Core" in result.output or "config.py" in result.output

    def test_checks_database_files(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["doctor"])

        assert result.exit_code == 0
        assert "Database" in result.output or "db" in result.output.lower()

    def test_checks_installed_apps(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["doctor"])

        assert result.exit_code == 0
        assert "Installed apps" in result.output or "users" in result.output

    def test_checks_environment(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["doctor"])

        assert result.exit_code == 0
        assert "Environment" in result.output or ".env" in result.output

    def test_fails_outside_project(self, tmp_path: Path, monkeypatch: Any) -> None:
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["doctor"])

        assert result.exit_code == 1
        assert "Could not find project root" in result.output

    def test_reports_missing_directories(self, minimal_project: Path, monkeypatch: Any) -> None:
        # Remove a required directory
        import shutil
        shutil.rmtree(minimal_project / "app" / "shared")
        monkeypatch.chdir(minimal_project)

        result = runner.invoke(app, ["doctor"])

        # Should report issues
        assert "Missing" in result.output or "issue" in result.output.lower()

    def test_reports_missing_files(self, minimal_project: Path, monkeypatch: Any) -> None:
        monkeypatch.chdir(minimal_project)

        result = runner.invoke(app, ["doctor"])

        # Should report missing files
        assert "Missing" in result.output

    def test_reports_invalid_installed_apps(self, complete_project: Path, monkeypatch: Any) -> None:
        # Add non-existent app to registry
        registry_path = complete_project / "app" / "core" / "registry.py"
        registry_path.write_text('''
INSTALLED_APPS: list[str] = [
    "nonexistent_app",
]
''')
        monkeypatch.chdir(complete_project)

        result = runner.invoke(app, ["doctor"])

        assert "nonexistent_app" in result.output or "not found" in result.output.lower()

    def test_shows_summary(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["doctor"])

        assert result.exit_code == 0
        # Should show some kind of summary
        assert "passed" in result.output.lower() or "issue" in result.output.lower() or "warning" in result.output.lower()

    def test_shows_suggestions_on_issues(self, minimal_project: Path, monkeypatch: Any) -> None:
        monkeypatch.chdir(minimal_project)

        result = runner.invoke(app, ["doctor"])

        # When there are issues, should show suggestions
        if "issue" in result.output.lower():
            assert "Suggestion" in result.output or "createapp" in result.output or ".env" in result.output


class TestDoctorCommandWithWarnings:
    """Tests for doctor command warning scenarios."""

    def test_warns_about_default_secret_key(self, complete_project: Path, monkeypatch: Any) -> None:
        # Set default secret key
        (complete_project / ".env").write_text('''
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=your-secret-key-change-in-production
''')
        monkeypatch.chdir(complete_project)

        result = runner.invoke(app, ["doctor"])

        # Should warn about default secret key
        assert "warning" in result.output.lower() or "default" in result.output.lower() or "change" in result.output.lower()

    def test_warns_about_missing_optional_files(self, complete_project: Path, monkeypatch: Any) -> None:
        # Remove optional file
        (complete_project / "app" / "core" / "security.py").unlink()
        monkeypatch.chdir(complete_project)

        result = runner.invoke(app, ["doctor"])

        # Should indicate optional file is missing but not fail
        assert result.exit_code == 0


class TestDoctorDiagnosticsOutput:
    """Tests for doctor command output formatting."""

    def test_uses_checkmarks_for_success(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["doctor"])

        # Should use checkmarks or similar for success
        assert "✓" in result.output or "OK" in result.output

    def test_uses_x_for_errors(self, minimal_project: Path, monkeypatch: Any) -> None:
        monkeypatch.chdir(minimal_project)

        result = runner.invoke(app, ["doctor"])

        # Should use X or similar for errors
        assert "✗" in result.output or "Missing" in result.output

    def test_categorizes_output(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["doctor"])

        # Output should be categorized
        categories = ["Directories", "Core", "Database", "apps", "Environment", "Main"]
        found_categories = sum(1 for cat in categories if cat in result.output)
        assert found_categories >= 3, "Should have multiple diagnostic categories"
