"""
Tests for template utilities.
"""

import pytest
from pathlib import Path
from typing import Any

from fastapi_new.utils.templates import (
    render_template,
    to_pascal_case,
    to_snake_case,
    to_singular,
    to_plural,
    create_app_context,
    create_project_context,
    get_template_path,
    render_template_file,
    copy_template_file,
    copy_template_directory,
    TEMPLATES_DIR,
)


class TestRenderTemplate:
    """Tests for render_template function."""

    def test_replaces_single_variable(self) -> None:
        content = "Hello {{name}}!"
        result = render_template(content, {"name": "World"})
        assert result == "Hello World!"

    def test_replaces_multiple_variables(self) -> None:
        content = "{{greeting}} {{name}}, welcome to {{place}}!"
        context = {"greeting": "Hello", "name": "User", "place": "FastAPI"}
        result = render_template(content, context)
        assert result == "Hello User, welcome to FastAPI!"

    def test_replaces_same_variable_multiple_times(self) -> None:
        content = "{{name}} likes {{name}}'s {{name}}"
        result = render_template(content, {"name": "Alice"})
        assert result == "Alice likes Alice's Alice"

    def test_leaves_unknown_variables_unchanged(self) -> None:
        content = "Hello {{name}}, your id is {{user_id}}"
        result = render_template(content, {"name": "Bob"})
        assert result == "Hello Bob, your id is {{user_id}}"

    def test_handles_empty_context(self) -> None:
        content = "Hello {{name}}!"
        result = render_template(content, {})
        assert result == "Hello {{name}}!"

    def test_handles_empty_content(self) -> None:
        result = render_template("", {"name": "Test"})
        assert result == ""

    def test_handles_content_without_variables(self) -> None:
        content = "No variables here"
        result = render_template(content, {"name": "Test"})
        assert result == "No variables here"

    def test_handles_multiline_content(self) -> None:
        content = """Line 1: {{var1}}
Line 2: {{var2}}
Line 3: {{var1}} and {{var2}}"""
        context = {"var1": "A", "var2": "B"}
        result = render_template(content, context)
        expected = """Line 1: A
Line 2: B
Line 3: A and B"""
        assert result == expected

    def test_converts_non_string_values_to_string(self) -> None:
        content = "Count: {{count}}, Active: {{active}}"
        result = render_template(content, {"count": 42, "active": True})
        assert result == "Count: 42, Active: True"


class TestToPascalCase:
    """Tests for to_pascal_case function."""

    def test_converts_snake_case(self) -> None:
        assert to_pascal_case("user_profile") == "UserProfile"
        assert to_pascal_case("order_items") == "OrderItems"
        assert to_pascal_case("my_app_name") == "MyAppName"

    def test_converts_kebab_case(self) -> None:
        assert to_pascal_case("user-profile") == "UserProfile"
        assert to_pascal_case("order-items") == "OrderItems"

    def test_converts_single_word(self) -> None:
        assert to_pascal_case("users") == "Users"
        assert to_pascal_case("product") == "Product"

    def test_converts_space_separated(self) -> None:
        assert to_pascal_case("user profile") == "UserProfile"
        assert to_pascal_case("my app") == "MyApp"

    def test_handles_already_pascal_case(self) -> None:
        assert to_pascal_case("UserProfile") == "Userprofile"  # It will lowercase then capitalize

    def test_handles_empty_string(self) -> None:
        assert to_pascal_case("") == ""

    def test_handles_mixed_separators(self) -> None:
        assert to_pascal_case("my_app-name test") == "MyAppNameTest"


class TestToSnakeCase:
    """Tests for to_snake_case function."""

    def test_converts_pascal_case(self) -> None:
        assert to_snake_case("UserProfile") == "user_profile"
        assert to_snake_case("OrderItems") == "order_items"

    def test_converts_camel_case(self) -> None:
        assert to_snake_case("userProfile") == "user_profile"
        assert to_snake_case("orderItems") == "order_items"

    def test_converts_kebab_case(self) -> None:
        assert to_snake_case("user-profile") == "user_profile"
        assert to_snake_case("order-items") == "order_items"

    def test_handles_single_word(self) -> None:
        assert to_snake_case("users") == "users"
        assert to_snake_case("Users") == "users"

    def test_handles_already_snake_case(self) -> None:
        assert to_snake_case("user_profile") == "user_profile"

    def test_handles_empty_string(self) -> None:
        assert to_snake_case("") == ""

    def test_handles_consecutive_capitals(self) -> None:
        assert to_snake_case("HTTPServer") == "http_server"
        assert to_snake_case("APIClient") == "api_client"


class TestToSingular:
    """Tests for to_singular function."""

    def test_converts_regular_plurals(self) -> None:
        assert to_singular("users") == "user"
        assert to_singular("products") == "product"
        assert to_singular("items") == "item"

    def test_converts_ies_plurals(self) -> None:
        assert to_singular("categories") == "category"
        assert to_singular("stories") == "story"

    def test_converts_es_plurals(self) -> None:
        assert to_singular("boxes") == "box"
        assert to_singular("buses") == "bus"

    def test_handles_words_ending_in_ss(self) -> None:
        # Words ending in 'ss' should not have 's' removed
        assert to_singular("class") == "class"
        assert to_singular("boss") == "boss"

    def test_handles_already_singular(self) -> None:
        assert to_singular("user") == "user"
        assert to_singular("item") == "item"

    def test_handles_empty_string(self) -> None:
        assert to_singular("") == ""


class TestToPlural:
    """Tests for to_plural function."""

    def test_converts_regular_words(self) -> None:
        assert to_plural("user") == "users"
        assert to_plural("product") == "products"

    def test_converts_words_ending_in_y(self) -> None:
        assert to_plural("category") == "categories"
        assert to_plural("story") == "stories"

    def test_handles_words_ending_in_vowel_y(self) -> None:
        assert to_plural("day") == "days"
        assert to_plural("key") == "keys"

    def test_converts_words_ending_in_s_x_z(self) -> None:
        assert to_plural("box") == "boxes"
        assert to_plural("bus") == "buses"
        assert to_plural("quiz") == "quizzes"
        assert to_plural("fizz") == "fizzzes"

    def test_converts_words_ending_in_ch_sh(self) -> None:
        assert to_plural("match") == "matches"
        assert to_plural("dish") == "dishes"

    def test_handles_empty_string(self) -> None:
        assert to_plural("") == ""  # Empty string returns empty


class TestCreateAppContext:
    """Tests for create_app_context function."""

    def test_creates_context_for_simple_name(self) -> None:
        context = create_app_context("users")
        assert context["app_name"] == "users"
        assert context["app_name_pascal"] == "Users"
        assert context["model_name"] == "User"
        assert context["table_name"] == "users"

    def test_creates_context_for_snake_case_name(self) -> None:
        context = create_app_context("order_items")
        assert context["app_name"] == "order_items"
        assert context["app_name_pascal"] == "OrderItems"
        assert context["model_name"] == "OrderItem"
        assert context["table_name"] == "order_items"

    def test_normalizes_pascal_case_input(self) -> None:
        context = create_app_context("UserProfile")
        assert context["app_name"] == "user_profile"
        assert context["app_name_pascal"] == "UserProfile"

    def test_normalizes_kebab_case_input(self) -> None:
        context = create_app_context("user-profile")
        assert context["app_name"] == "user_profile"
        assert context["app_name_pascal"] == "UserProfile"

    def test_includes_description(self) -> None:
        context = create_app_context("products")
        assert "app_description" in context
        assert "Products" in context["app_description"]


class TestCreateProjectContext:
    """Tests for create_project_context function."""

    def test_creates_context_for_simple_name(self) -> None:
        context = create_project_context("myproject")
        assert context["project_name"] == "myproject"
        assert context["project_name_snake"] == "myproject"
        assert context["project_name_pascal"] == "Myproject"

    def test_creates_context_for_hyphenated_name(self) -> None:
        context = create_project_context("my-project")
        assert context["project_name"] == "my-project"
        assert context["project_name_snake"] == "my_project"
        assert context["project_name_pascal"] == "MyProject"

    def test_creates_context_for_underscored_name(self) -> None:
        context = create_project_context("my_awesome_project")
        assert context["project_name"] == "my_awesome_project"
        assert context["project_name_snake"] == "my_awesome_project"
        assert context["project_name_pascal"] == "MyAwesomeProject"


class TestGetTemplatePath:
    """Tests for get_template_path function."""

    def test_returns_path_for_project_templates(self) -> None:
        path = get_template_path("project")
        assert path == TEMPLATES_DIR / "project"

    def test_returns_path_for_app_templates(self) -> None:
        path = get_template_path("app")
        assert path == TEMPLATES_DIR / "app"

    def test_returns_path_for_db_templates(self) -> None:
        path = get_template_path("db")
        assert path == TEMPLATES_DIR / "db"


class TestRenderTemplateFile:
    """Tests for render_template_file function."""

    def test_renders_template_from_file(self, tmp_path: Path) -> None:
        # Create a temporary template file
        template_file = tmp_path / "test.tpl"
        template_file.write_text("Hello {{name}}! Welcome to {{place}}.")

        result = render_template_file(template_file, {"name": "User", "place": "FastAPI"})
        assert result == "Hello User! Welcome to FastAPI."

    def test_handles_multiline_template_file(self, tmp_path: Path) -> None:
        template_file = tmp_path / "multiline.tpl"
        template_file.write_text("""Line 1: {{var1}}
Line 2: {{var2}}""")

        result = render_template_file(template_file, {"var1": "A", "var2": "B"})
        assert "Line 1: A" in result
        assert "Line 2: B" in result


class TestCopyTemplateFile:
    """Tests for copy_template_file function."""

    def test_copies_and_renders_template(self, tmp_path: Path) -> None:
        # Create source template
        source = tmp_path / "source" / "test.tpl"
        source.parent.mkdir(parents=True)
        source.write_text("Project: {{project_name}}")

        # Copy to destination
        dest = tmp_path / "dest" / "test.py"
        copy_template_file(source, dest, {"project_name": "awesome"})

        assert dest.exists()
        assert dest.read_text() == "Project: awesome"

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        source = tmp_path / "source.tpl"
        source.write_text("Content")

        dest = tmp_path / "deep" / "nested" / "path" / "file.py"
        copy_template_file(source, dest, {})

        assert dest.exists()
        assert dest.parent.exists()


class TestCopyTemplateDirectory:
    """Tests for copy_template_directory function."""

    def test_copies_all_template_files(self, tmp_path: Path, monkeypatch: Any) -> None:
        # Create a mock template directory
        mock_templates = tmp_path / "templates"
        mock_app_dir = mock_templates / "app"
        mock_app_dir.mkdir(parents=True)

        # Create mock template files
        (mock_app_dir / "__init__.py.tpl").write_text("# {{app_name}}")
        (mock_app_dir / "models.py.tpl").write_text("# Models for {{app_name}}")

        # Monkeypatch TEMPLATES_DIR
        monkeypatch.setattr("fastapi_new.utils.templates.TEMPLATES_DIR", mock_templates)

        # Copy templates
        dest = tmp_path / "output"
        created = copy_template_directory("app", dest, {"app_name": "users"})

        assert len(created) == 2
        assert (dest / "__init__.py").exists()
        assert (dest / "models.py").exists()
        assert "# users" in (dest / "__init__.py").read_text()

    def test_preserves_directory_structure(self, tmp_path: Path, monkeypatch: Any) -> None:
        # Create mock template directory with nested structure
        mock_templates = tmp_path / "templates"
        mock_project = mock_templates / "project"
        (mock_project / "core").mkdir(parents=True)
        (mock_project / "db").mkdir(parents=True)

        (mock_project / "main.py.tpl").write_text("# Main")
        (mock_project / "core" / "config.py.tpl").write_text("# Config")
        (mock_project / "db" / "base.py.tpl").write_text("# Base")

        monkeypatch.setattr("fastapi_new.utils.templates.TEMPLATES_DIR", mock_templates)

        dest = tmp_path / "output"
        created = copy_template_directory("project", dest, {})

        assert (dest / "main.py").exists()
        assert (dest / "core" / "config.py").exists()
        assert (dest / "db" / "base.py").exists()


class TestTemplateFilesExist:
    """Tests to verify template files exist."""

    def test_project_templates_exist(self) -> None:
        project_path = TEMPLATES_DIR / "project"
        assert project_path.exists(), "Project templates directory should exist"

        # Check key files
        assert (project_path / "main.py.tpl").exists()
        assert (project_path / "core" / "config.py.tpl").exists()
        assert (project_path / "core" / "registry.py.tpl").exists()

    def test_app_templates_exist(self) -> None:
        app_path = TEMPLATES_DIR / "app"
        assert app_path.exists(), "App templates directory should exist"

        # Check MSSR files
        expected_files = [
            "__init__.py.tpl",
            "models.py.tpl",
            "schemas.py.tpl",
            "services.py.tpl",
            "repositories.py.tpl",
            "routes.py.tpl",
            "dependencies.py.tpl",
        ]

        for file_name in expected_files:
            assert (app_path / file_name).exists(), f"{file_name} should exist"
