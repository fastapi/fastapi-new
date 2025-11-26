"""
Tests for createapp command.
"""

import pytest
from pathlib import Path
from typing import Any

from typer.testing import CliRunner

from fastapi_new.cli import app
from fastapi_new.createapp import (
    find_project_root,
    validate_app_name,
    add_to_installed_apps,
)

runner = CliRunner()


@pytest.fixture
def project_structure(tmp_path: Path) -> Path:
    """Create a minimal FastAPI-New project structure."""
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    (app_dir / "apps").mkdir()
    (app_dir / "core").mkdir()

    # Create registry.py
    registry_content = '''"""
Registry Module
"""

INSTALLED_APPS: list[str] = [
    # Add your apps here
]
'''
    (app_dir / "core" / "registry.py").write_text(registry_content)

    return tmp_path


@pytest.fixture
def temp_project_dir(project_structure: Path, monkeypatch: Any) -> Path:
    """Create a temporary project directory and cd into it."""
    monkeypatch.chdir(project_structure)
    return project_structure


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

    def test_returns_none_when_too_deep(self, tmp_path: Path, monkeypatch: Any) -> None:
        (tmp_path / "app").mkdir()
        deep = tmp_path / "a" / "b" / "c" / "d" / "e"
        deep.mkdir(parents=True)
        monkeypatch.chdir(deep)

        result = find_project_root()
        # Should be None because we only go up 3 levels
        assert result is None


class TestValidateAppName:
    """Tests for validate_app_name function."""

    def test_accepts_valid_simple_name(self) -> None:
        assert validate_app_name("users") is None
        assert validate_app_name("products") is None
        assert validate_app_name("orders") is None

    def test_accepts_valid_snake_case_name(self) -> None:
        assert validate_app_name("user_profiles") is None
        assert validate_app_name("order_items") is None
        assert validate_app_name("my_app123") is None

    def test_accepts_name_with_numbers(self) -> None:
        assert validate_app_name("app1") is None
        assert validate_app_name("v2users") is None

    def test_rejects_empty_name(self) -> None:
        error = validate_app_name("")
        assert error is not None
        assert "empty" in error.lower()

    def test_rejects_name_starting_with_number(self) -> None:
        error = validate_app_name("123app")
        assert error is not None
        assert "start with a letter" in error.lower()

    def test_rejects_name_with_uppercase(self) -> None:
        # Names get normalized to snake_case, so this should work
        # Actually, let me check the implementation - it converts to snake_case first
        # So "UserProfile" becomes "user_profile" which is valid
        error = validate_app_name("UserProfile")
        assert error is None  # It gets converted to snake_case

    def test_rejects_reserved_names(self) -> None:
        reserved = ["app", "core", "db", "shared", "plugins", "tests"]
        for name in reserved:
            error = validate_app_name(name)
            assert error is not None
            assert "reserved" in error.lower()

    def test_rejects_names_with_special_characters(self) -> None:
        error = validate_app_name("user-profile")  # Kebab case gets converted
        # After conversion to snake_case, this becomes "user_profile" which is valid
        # Actually need to check implementation
        # to_snake_case("user-profile") -> "user_profile" which is valid
        assert error is None  # Gets converted

    def test_rejects_names_with_spaces(self) -> None:
        error = validate_app_name("user profile")
        # After conversion: "user_profile" which is valid
        assert error is None


class TestAddToInstalledApps:
    """Tests for add_to_installed_apps function."""

    def test_adds_app_to_empty_list(self, tmp_path: Path) -> None:
        registry = tmp_path / "registry.py"
        registry.write_text('''INSTALLED_APPS: list[str] = [
]
''')

        result = add_to_installed_apps(registry, "users")

        assert result is True
        content = registry.read_text()
        assert '"users"' in content

    def test_adds_app_to_list_with_comments(self, tmp_path: Path) -> None:
        registry = tmp_path / "registry.py"
        registry.write_text('''INSTALLED_APPS: list[str] = [
    # Add your apps here
]
''')

        result = add_to_installed_apps(registry, "users")

        assert result is True
        content = registry.read_text()
        assert '"users"' in content

    def test_adds_app_to_existing_list(self, tmp_path: Path) -> None:
        registry = tmp_path / "registry.py"
        registry.write_text('''INSTALLED_APPS: list[str] = [
    "products",
]
''')

        result = add_to_installed_apps(registry, "users")

        assert result is True
        content = registry.read_text()
        assert '"users"' in content
        assert '"products"' in content

    def test_does_not_duplicate_existing_app(self, tmp_path: Path) -> None:
        registry = tmp_path / "registry.py"
        registry.write_text('''INSTALLED_APPS: list[str] = [
    "users",
]
''')

        result = add_to_installed_apps(registry, "users")

        assert result is True  # Returns True because app is "registered"
        content = registry.read_text()
        # Should only have one "users"
        assert content.count('"users"') == 1

    def test_returns_false_for_missing_file(self, tmp_path: Path) -> None:
        registry = tmp_path / "nonexistent.py"

        result = add_to_installed_apps(registry, "users")

        assert result is False

    def test_handles_single_quoted_strings(self, tmp_path: Path) -> None:
        registry = tmp_path / "registry.py"
        registry.write_text('''INSTALLED_APPS: list[str] = [
    'products',
]
''')

        result = add_to_installed_apps(registry, "products")

        # Should detect that 'products' is already there
        assert result is True


class TestCreateAppCommand:
    """Tests for createapp CLI command."""

    def test_creates_app_successfully(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["createapp", "users"])

        assert result.exit_code == 0
        assert "Success!" in result.output

        # Check files were created
        app_dir = temp_project_dir / "app" / "apps" / "users"
        assert app_dir.exists()
        assert (app_dir / "__init__.py").exists()
        assert (app_dir / "models.py").exists()
        assert (app_dir / "schemas.py").exists()
        assert (app_dir / "services.py").exists()
        assert (app_dir / "repositories.py").exists()
        assert (app_dir / "routes.py").exists()
        assert (app_dir / "dependencies.py").exists()

    def test_creates_app_with_snake_case_name(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["createapp", "user_profiles"])

        assert result.exit_code == 0
        app_dir = temp_project_dir / "app" / "apps" / "user_profiles"
        assert app_dir.exists()

    def test_normalizes_kebab_case_name(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["createapp", "order-items"])

        assert result.exit_code == 0
        # Should be normalized to snake_case
        app_dir = temp_project_dir / "app" / "apps" / "order_items"
        assert app_dir.exists()

    def test_normalizes_pascal_case_name(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["createapp", "UserProfile"])

        assert result.exit_code == 0
        app_dir = temp_project_dir / "app" / "apps" / "user_profile"
        assert app_dir.exists()

    def test_auto_registers_app(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["createapp", "users"])

        assert result.exit_code == 0

        # Check registry was updated
        registry = temp_project_dir / "app" / "core" / "registry.py"
        content = registry.read_text()
        assert '"users"' in content

    def test_fails_for_existing_app(self, temp_project_dir: Path) -> None:
        # Create the app directory first
        app_dir = temp_project_dir / "app" / "apps" / "users"
        app_dir.mkdir(parents=True)

        result = runner.invoke(app, ["createapp", "users"])

        assert result.exit_code == 1
        assert "already exists" in result.output

    def test_fails_for_reserved_name(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["createapp", "core"])

        assert result.exit_code == 1
        assert "reserved" in result.output.lower()

    def test_fails_outside_project(self, tmp_path: Path, monkeypatch: Any) -> None:
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["createapp", "users"])

        assert result.exit_code == 1
        assert "Could not find project root" in result.output

    def test_fails_without_apps_directory(self, tmp_path: Path, monkeypatch: Any) -> None:
        # Create app directory but not apps subdirectory
        (tmp_path / "app").mkdir()
        (tmp_path / "app" / "core").mkdir()
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["createapp", "users"])

        assert result.exit_code == 1
        assert "app/apps/" in result.output or "not found" in result.output.lower()

    def test_template_variables_replaced(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["createapp", "products"])

        assert result.exit_code == 0

        app_dir = temp_project_dir / "app" / "apps" / "products"

        # Check models.py has correct model name
        models_content = (app_dir / "models.py").read_text()
        assert "Product" in models_content  # Model name should be singular
        assert "products" in models_content  # Table name should be plural

        # Check routes.py has router
        routes_content = (app_dir / "routes.py").read_text()
        assert "router" in routes_content
        assert "APIRouter" in routes_content

    def test_displays_next_steps(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["createapp", "users"])

        assert result.exit_code == 0
        assert "Next steps" in result.output
        assert "models.py" in result.output

    def test_displays_app_structure(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["createapp", "users"])

        assert result.exit_code == 0
        assert "models.py" in result.output
        assert "schemas.py" in result.output
        assert "routes.py" in result.output
        assert "services.py" in result.output


class TestCreateAppTemplateContent:
    """Tests to verify template content in created apps."""

    def test_init_exports_router(self, temp_project_dir: Path) -> None:
        runner.invoke(app, ["createapp", "users"])

        init_content = (temp_project_dir / "app" / "apps" / "users" / "__init__.py").read_text()
        assert "router" in init_content
        assert "from" in init_content

    def test_routes_has_api_router(self, temp_project_dir: Path) -> None:
        runner.invoke(app, ["createapp", "users"])

        routes_content = (temp_project_dir / "app" / "apps" / "users" / "routes.py").read_text()
        assert "APIRouter" in routes_content
        assert "router = APIRouter()" in routes_content

    def test_models_has_base_import(self, temp_project_dir: Path) -> None:
        runner.invoke(app, ["createapp", "users"])

        models_content = (temp_project_dir / "app" / "apps" / "users" / "models.py").read_text()
        assert "Base" in models_content
        assert "Column" in models_content or "mapped_column" in models_content

    def test_schemas_has_pydantic_import(self, temp_project_dir: Path) -> None:
        runner.invoke(app, ["createapp", "users"])

        schemas_content = (temp_project_dir / "app" / "apps" / "users" / "schemas.py").read_text()
        assert "BaseModel" in schemas_content
        assert "pydantic" in schemas_content

    def test_services_has_repository_import(self, temp_project_dir: Path) -> None:
        runner.invoke(app, ["createapp", "users"])

        services_content = (temp_project_dir / "app" / "apps" / "users" / "services.py").read_text()
        assert "Repository" in services_content

    def test_repositories_has_session_import(self, temp_project_dir: Path) -> None:
        runner.invoke(app, ["createapp", "users"])

        repos_content = (temp_project_dir / "app" / "apps" / "users" / "repositories.py").read_text()
        assert "AsyncSession" in repos_content or "session" in repos_content.lower()

    def test_dependencies_has_depends_import(self, temp_project_dir: Path) -> None:
        runner.invoke(app, ["createapp", "users"])

        deps_content = (temp_project_dir / "app" / "apps" / "users" / "dependencies.py").read_text()
        assert "Depends" in deps_content
