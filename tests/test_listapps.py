"""
Tests for list command.
"""

import pytest
from pathlib import Path
from typing import Any

from typer.testing import CliRunner

from fastapi_new.cli import app
from fastapi_new.listapps import (
    find_project_root,
    get_installed_apps,
    get_app_directories,
    get_app_info,
)

runner = CliRunner()


@pytest.fixture
def project_structure(tmp_path: Path) -> Path:
    """Create a minimal FastAPI-New project structure."""
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    (app_dir / "apps").mkdir()
    (app_dir / "core").mkdir()

    # Create registry.py with some installed apps
    registry_content = '''"""
Registry Module
"""

INSTALLED_APPS: list[str] = [
    "users",
    "products",
]
'''
    (app_dir / "core" / "registry.py").write_text(registry_content)

    return tmp_path


@pytest.fixture
def project_with_apps(project_structure: Path) -> Path:
    """Create a project with actual app directories."""
    apps_dir = project_structure / "app" / "apps"

    # Create users app with all files
    users_dir = apps_dir / "users"
    users_dir.mkdir()
    (users_dir / "__init__.py").write_text("from .routes import router")
    (users_dir / "models.py").write_text("# Models")
    (users_dir / "schemas.py").write_text("# Schemas")
    (users_dir / "services.py").write_text("# Services")
    (users_dir / "repositories.py").write_text("# Repositories")
    (users_dir / "routes.py").write_text("from fastapi import APIRouter\nrouter = APIRouter()")
    (users_dir / "dependencies.py").write_text("# Dependencies")

    # Create products app with some files missing
    products_dir = apps_dir / "products"
    products_dir.mkdir()
    (products_dir / "__init__.py").write_text("from .routes import router")
    (products_dir / "routes.py").write_text("from fastapi import APIRouter\nrouter = APIRouter()")
    (products_dir / "models.py").write_text("# Models")

    # Create unregistered app
    orders_dir = apps_dir / "orders"
    orders_dir.mkdir()
    (orders_dir / "__init__.py").write_text("from .routes import router")
    (orders_dir / "routes.py").write_text("from fastapi import APIRouter\nrouter = APIRouter()")

    return project_structure


@pytest.fixture
def temp_project_dir(project_with_apps: Path, monkeypatch: Any) -> Path:
    """Create a temporary project directory and cd into it."""
    monkeypatch.chdir(project_with_apps)
    return project_with_apps


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

    def test_returns_none_when_no_project(self, tmp_path: Path, monkeypatch: Any) -> None:
        monkeypatch.chdir(tmp_path)

        result = find_project_root()
        assert result is None


class TestGetInstalledApps:
    """Tests for get_installed_apps function."""

    def test_returns_apps_from_registry(self, project_structure: Path) -> None:
        registry_path = project_structure / "app" / "core" / "registry.py"

        apps = get_installed_apps(registry_path)

        assert "users" in apps
        assert "products" in apps
        assert len(apps) == 2

    def test_returns_empty_list_for_missing_file(self, tmp_path: Path) -> None:
        registry_path = tmp_path / "nonexistent.py"

        apps = get_installed_apps(registry_path)

        assert apps == []

    def test_returns_empty_list_for_empty_registry(self, tmp_path: Path) -> None:
        registry_path = tmp_path / "registry.py"
        registry_path.write_text('''INSTALLED_APPS: list[str] = [
]
''')

        apps = get_installed_apps(registry_path)

        assert apps == []

    def test_handles_single_quoted_strings(self, tmp_path: Path) -> None:
        registry_path = tmp_path / "registry.py"
        registry_path.write_text('''INSTALLED_APPS: list[str] = [
    'users',
    'products',
]
''')

        apps = get_installed_apps(registry_path)

        assert "users" in apps
        assert "products" in apps

    def test_handles_comments_in_list(self, tmp_path: Path) -> None:
        registry_path = tmp_path / "registry.py"
        registry_path.write_text('''INSTALLED_APPS: list[str] = [
    # Core apps
    "users",
    # E-commerce
    "products",
]
''')

        apps = get_installed_apps(registry_path)

        assert len(apps) == 2
        assert "users" in apps
        assert "products" in apps

    def test_handles_no_installed_apps_list(self, tmp_path: Path) -> None:
        registry_path = tmp_path / "registry.py"
        registry_path.write_text("# No INSTALLED_APPS here")

        apps = get_installed_apps(registry_path)

        assert apps == []


class TestGetAppDirectories:
    """Tests for get_app_directories function."""

    def test_returns_app_directories(self, project_with_apps: Path) -> None:
        apps_dir = project_with_apps / "app" / "apps"

        directories = get_app_directories(apps_dir)

        assert "users" in directories
        assert "products" in directories
        assert "orders" in directories

    def test_returns_empty_list_for_missing_directory(self, tmp_path: Path) -> None:
        apps_dir = tmp_path / "nonexistent"

        directories = get_app_directories(apps_dir)

        assert directories == []

    def test_ignores_files(self, tmp_path: Path) -> None:
        apps_dir = tmp_path / "apps"
        apps_dir.mkdir()
        (apps_dir / "__init__.py").write_text("")
        (apps_dir / "some_file.py").write_text("")

        directories = get_app_directories(apps_dir)

        assert directories == []

    def test_ignores_private_directories(self, tmp_path: Path) -> None:
        apps_dir = tmp_path / "apps"
        apps_dir.mkdir()

        # Private directory (starts with underscore)
        private_dir = apps_dir / "_private"
        private_dir.mkdir()
        (private_dir / "__init__.py").write_text("")

        # Regular directory
        users_dir = apps_dir / "users"
        users_dir.mkdir()
        (users_dir / "__init__.py").write_text("")

        directories = get_app_directories(apps_dir)

        assert "users" in directories
        assert "_private" not in directories

    def test_ignores_directories_without_init(self, tmp_path: Path) -> None:
        apps_dir = tmp_path / "apps"
        apps_dir.mkdir()

        # Directory without __init__.py or routes.py
        empty_dir = apps_dir / "empty"
        empty_dir.mkdir()

        # Directory with routes.py
        valid_dir = apps_dir / "valid"
        valid_dir.mkdir()
        (valid_dir / "routes.py").write_text("")

        directories = get_app_directories(apps_dir)

        assert "valid" in directories
        assert "empty" not in directories

    def test_returns_sorted_list(self, tmp_path: Path) -> None:
        apps_dir = tmp_path / "apps"
        apps_dir.mkdir()

        for name in ["zebra", "alpha", "middle"]:
            dir_path = apps_dir / name
            dir_path.mkdir()
            (dir_path / "__init__.py").write_text("")

        directories = get_app_directories(apps_dir)

        assert directories == ["alpha", "middle", "zebra"]


class TestGetAppInfo:
    """Tests for get_app_info function."""

    def test_returns_all_files_info(self, project_with_apps: Path) -> None:
        app_dir = project_with_apps / "app" / "apps" / "users"

        info = get_app_info(app_dir)

        assert info["has_models"] is True
        assert info["has_schemas"] is True
        assert info["has_services"] is True
        assert info["has_repositories"] is True
        assert info["has_routes"] is True
        assert info["has_dependencies"] is True

    def test_returns_partial_files_info(self, project_with_apps: Path) -> None:
        app_dir = project_with_apps / "app" / "apps" / "products"

        info = get_app_info(app_dir)

        assert info["has_models"] is True
        assert info["has_schemas"] is False
        assert info["has_services"] is False
        assert info["has_repositories"] is False
        assert info["has_routes"] is True
        assert info["has_dependencies"] is False

    def test_returns_false_for_all_missing_files(self, tmp_path: Path) -> None:
        app_dir = tmp_path / "empty_app"
        app_dir.mkdir()

        info = get_app_info(app_dir)

        assert info["has_models"] is False
        assert info["has_schemas"] is False
        assert info["has_services"] is False
        assert info["has_repositories"] is False
        assert info["has_routes"] is False
        assert info["has_dependencies"] is False


class TestListCommand:
    """Tests for list CLI command."""

    def test_lists_apps_successfully(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "users" in result.output
        assert "products" in result.output

    def test_shows_registered_status(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        # Users and products are registered
        assert "registered" in result.output.lower()

    def test_shows_unregistered_apps(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        # Orders is in apps dir but not in INSTALLED_APPS
        assert "orders" in result.output
        assert "not registered" in result.output.lower()

    def test_shows_total_count(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "3" in result.output or "Total" in result.output

    def test_verbose_shows_file_info(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["list", "--verbose"])

        assert result.exit_code == 0
        # Should show file information
        assert "models" in result.output.lower() or "Files" in result.output

    def test_verbose_short_flag(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["list", "-v"])

        assert result.exit_code == 0

    def test_fails_outside_project(self, tmp_path: Path, monkeypatch: Any) -> None:
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 1
        assert "Could not find project root" in result.output

    def test_shows_hint_for_no_apps(self, project_structure: Path, monkeypatch: Any) -> None:
        # Use project structure without app directories
        monkeypatch.chdir(project_structure)

        result = runner.invoke(app, ["list"])

        # Should either show no apps message or hint to create
        assert result.exit_code == 0
        assert "No apps" in result.output or "createapp" in result.output

    def test_shows_registration_hint(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["list"])

        # If there are unregistered apps, should show hint
        if "not registered" in result.output.lower():
            assert "INSTALLED_APPS" in result.output or "registry" in result.output.lower()

    def test_shows_apps_directory_path(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "apps" in result.output.lower()


class TestListCommandWithEmptyProject:
    """Tests for list command with no apps."""

    def test_handles_empty_apps_directory(self, project_structure: Path, monkeypatch: Any) -> None:
        monkeypatch.chdir(project_structure)

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "No apps" in result.output or "createapp" in result.output

    def test_suggests_createapp_command(self, project_structure: Path, monkeypatch: Any) -> None:
        monkeypatch.chdir(project_structure)

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "createapp" in result.output


class TestListCommandSummary:
    """Tests for list command summary output."""

    def test_shows_registered_count(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        # Should show count of registered apps (2 in our fixture)
        assert "2" in result.output or "Registered" in result.output

    def test_shows_unregistered_count(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        # Should indicate there's 1 unregistered app (orders)
        assert "1" in result.output or "not registered" in result.output.lower()
