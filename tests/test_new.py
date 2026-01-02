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


def _assert_project_created(project_path: Path) -> None:
    assert (project_path / "main.py").exists()
    assert (project_path / "README.md").exists()
    assert (project_path / "pyproject.toml").exists()


def test_creates_project_successfully(temp_project_dir: Path) -> None:
    result = runner.invoke(app, ["my_fastapi_project"])

    assert result.exit_code == 0
    project_path = temp_project_dir / "my_fastapi_project"
    _assert_project_created(project_path)
    assert "Success!" in result.output
    assert "my_fastapi_project" in result.output


def test_creates_project_with_python_version(temp_project_dir: Path) -> None:
    # Test long form
    result = runner.invoke(app, ["project_long", "--python", "3.12"])
    assert result.exit_code == 0
    project_path = temp_project_dir / "project_long"
    _assert_project_created(project_path)
    assert "3.12" in (project_path / "pyproject.toml").read_text()

    # Test short form
    result = runner.invoke(app, ["project_short", "-p", "3.11"])
    assert result.exit_code == 0
    project_path = temp_project_dir / "project_short"
    assert "3.11" in (project_path / "pyproject.toml").read_text()


def test_validates_template_file_contents(temp_project_dir: Path) -> None:
    result = runner.invoke(app, ["sample_project"])
    assert result.exit_code == 0

    project_path = temp_project_dir / "sample_project"

    main_py_content = (project_path / "main.py").read_text()
    assert "from fastapi import FastAPI" in main_py_content
    assert "app = FastAPI()" in main_py_content

    # Check README.md
    readme_content = (project_path / "README.md").read_text()
    assert "# sample_project" in readme_content
    assert "A project created with FastAPI" in readme_content

    # Check pyproject.toml
    pyproject_content = (project_path / "pyproject.toml").read_text()
    assert 'name = "sample-project"' in pyproject_content
    assert "fastapi[standard]" in pyproject_content


def test_initializes_in_current_directory(temp_project_dir: Path) -> None:
    result = runner.invoke(app, [])

    assert result.exit_code == 0
    assert "Initializing in current directory" in result.output
    _assert_project_created(temp_project_dir)


def test_initializes_in_current_directory_with_dot(temp_project_dir: Path) -> None:
    result = runner.invoke(app, ["."])

    assert result.exit_code == 0
    assert "Initializing in current directory" in result.output
    _assert_project_created(temp_project_dir)

    readme_content = (temp_project_dir / "README.md").read_text()
    assert f"# {temp_project_dir.name}" in readme_content


def test_rejects_existing_directory(temp_project_dir: Path) -> None:
    existing_dir = temp_project_dir / "existing_project"
    existing_dir.mkdir()

    result = runner.invoke(app, ["existing_project"])
    assert result.exit_code == 1
    assert "Directory 'existing_project' already exists." in result.output


def test_rejects_python_below_3_10(temp_project_dir: Path) -> None:
    result = runner.invoke(app, ["test_project", "--python", "3.9"])
    assert result.exit_code == 1
    assert "Python 3.9 is not supported" in result.output
    assert "FastAPI requires Python 3.10" in result.output


def test_passes_single_digit_python_version_to_uv(temp_project_dir: Path) -> None:
    result = runner.invoke(app, ["test_project", "--python", "3"])
    assert result.exit_code == 0
    project_path = temp_project_dir / "test_project"
    _assert_project_created(project_path)


def test_passes_malformed_python_version_to_uv(temp_project_dir: Path) -> None:
    result = runner.invoke(app, ["test_project", "--python", "abc.def"])
    # uv will reject this, we just verify we don't crash during validation
    assert result.exit_code == 1


def test_creates_project_without_python_flag(temp_project_dir: Path) -> None:
    result = runner.invoke(app, ["test_project"])
    assert result.exit_code == 0
    project_path = temp_project_dir / "test_project"
    _assert_project_created(project_path)


def test_failed_to_initialize_with_uv(monkeypatch: Any) -> None:
    def mock_run(*args: Any, **kwargs: Any) -> None:
        # Let the first check for 'uv' succeed, but fail on 'uv init'
        if args[0][0] == "uv" and args[0][1] == "init":
            raise subprocess.CalledProcessError(
                1, args[0], stderr=b"uv init failed for some reason"
            )

    monkeypatch.setattr(subprocess, "run", mock_run)

    result = runner.invoke(app, ["failing_project"])
    assert result.exit_code == 1
    assert "Failed to initialize project with uv" in result.output


def test_failed_to_add_dependencies(temp_project_dir: Path, monkeypatch: Any) -> None:
    def mock_run(*args: Any, **kwargs: Any) -> None:
        # Let 'uv init' succeed, but fail on 'uv add'
        if args[0][0] == "uv" and args[0][1] == "add":
            raise subprocess.CalledProcessError(
                1, args[0], stderr=b"Failed to resolve dependencies"
            )

    monkeypatch.setattr(subprocess, "run", mock_run)

    result = runner.invoke(app, ["failing_deps"])
    assert result.exit_code == 1
    assert "Failed to install dependencies" in result.output


def test_file_write_failure(temp_project_dir: Path, monkeypatch: Any) -> None:
    original_write_text = Path.write_text

    def mock_write_text(self: Path, *args: Any, **kwargs: Any) -> None:
        # Fail when trying to write README.md (let main.py succeed first)
        if self.name == "README.md":
            raise PermissionError("Permission denied")
        original_write_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", mock_write_text)

    result = runner.invoke(app, ["test_write_fail"])
    assert result.exit_code == 1
    assert "Failed to write template files" in result.output


def test_uv_not_installed(temp_project_dir: Path, monkeypatch: Any) -> None:
    monkeypatch.setattr(shutil, "which", lambda _: None)

    result = runner.invoke(app, ["test_uv_missing_project"])
    assert result.exit_code == 1
    assert "uv is required to create new projects" in result.output
    assert "https://docs.astral.sh/uv/" in result.output
