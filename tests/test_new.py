from fastapi_new.cli import app
from pathlib import Path
from typer.testing import CliRunner
from unittest.mock import MagicMock
import pytest
import shutil

runner = CliRunner()


@pytest.fixture
def temp_project_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    return tmp_path


def _assert_common_files(project_path: Path) -> None:
    assert (project_path / "main.py").exists()
    assert (project_path / "README.md").exists()
    assert (project_path / "requirements.txt").exists()
    # pyproject.toml dibuat oleh uv init
    assert (project_path / "pyproject.toml").exists()


def test_wizard_advanced_structure(temp_project_dir: Path) -> None:
    user_inputs = "my_laravel_app\n2\n1\ny\ny\n"
    result = runner.invoke(app, [], input=user_inputs)

    assert result.exit_code == 0
    project_path = temp_project_dir / "my_laravel_app"

    _assert_common_files(project_path)
    assert "Created project: my_laravel_app" in result.output

    assert (project_path / "app" / "controllers").exists()
    assert (project_path / "app" / "models").exists()
    assert (project_path / "database" / "migrations").exists()

    assert (project_path / "views" / "html" / "index.html").exists()
    assert (project_path / "views" / "css" / "style.css").exists()

    assert (project_path / "tests" / "test_main.py").exists()


def test_wizard_simple_structure(temp_project_dir: Path) -> None:
    user_inputs = "my_simple_app\n1\n3\nn\nn\n"
    result = runner.invoke(app, [], input=user_inputs)

    assert result.exit_code == 0
    project_path = temp_project_dir / "my_simple_app"

    _assert_common_files(project_path)

    # Pastikan struktur Advanced TIDAK ada
    assert not (project_path / "app").exists()
    assert not (project_path / "views").exists()
    assert not (project_path / "database").exists()


def test_arg_mode_defaults_to_simple(temp_project_dir: Path) -> None:
    result = runner.invoke(app, ["fast_project"])

    assert result.exit_code == 0
    project_path = temp_project_dir / "fast_project"

    _assert_common_files(project_path)
    assert not (project_path / "app").exists()


def test_validates_template_content(temp_project_dir: Path) -> None:
    user_inputs = "check_content\n1\n3\nn\nn\n"
    runner.invoke(app, [], input=user_inputs)

    project_path = temp_project_dir / "check_content"

    main_py = (project_path / "main.py").read_text()
    assert "from fastapi import FastAPI" in main_py
    assert "Welcome to your FastAPI project!" in main_py

    readme = (project_path / "README.md").read_text()
    assert "# check_content" in readme
    assert "app/controllers" in readme


def test_rejects_existing_directory(temp_project_dir: Path) -> None:
    (temp_project_dir / "double_project").mkdir()

    user_inputs = "double_project\n"
    result = runner.invoke(app, [], input=user_inputs)

    assert result.exit_code == 1
    assert "already exists" in result.output


def test_uv_not_installed(temp_project_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(shutil, "which", MagicMock(return_value=None))

    user_inputs = "no_uv_proj\n"
    result = runner.invoke(app, [], input=user_inputs)

    assert result.exit_code == 1
    assert "uv is required" in result.output

    project_path = temp_project_dir / "no_uv_proj"
    assert not project_path.exists()