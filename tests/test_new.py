from fastapi_new.cli import app
from pathlib import Path
from typer.testing import CliRunner
from unittest.mock import MagicMock
import pytest
import shutil

runner = CliRunner()


@pytest.fixture
def temp_project_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create a temporary directory and cd into it."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


def _assert_common_files(project_path: Path) -> None:
    """Check the basic files that must always be present."""
    assert (project_path / "main.py").exists()
    assert (project_path / "README.md").exists()
    assert (project_path / "requirements.txt").exists()
    assert (project_path / ".gitignore").exists()
    assert (project_path / "pyproject.toml").exists()


def test_wizard_full_features(temp_project_dir: Path) -> None:
    """
    Simulation test 'All-in-One': 
    Advanced + SQLModel + Ruff + Views + Tests.

    Input Order:
    1. Name: 'full_app'
    2. Arch: '2' (Advanced)
    3. ORM: '1' (SQLModel)
    4. Lint: '1' (Ruff)
    5. View: 'y'
    6. Test: 'y'
    """
    user_inputs = "full_app\n2\n1\n1\ny\ny\n"
    result = runner.invoke(app, [], input=user_inputs)

    assert result.exit_code == 0
    project_path = temp_project_dir / "full_app"

    _assert_common_files(project_path)

    assert (project_path / "app" / "controllers").exists()
    assert (project_path / "database" / "migrations").exists()

    assert (project_path / "config" / "database.py").exists()
    assert (project_path / ".env").exists()

    gitignore_content = (project_path / ".gitignore").read_text()
    assert ".env" in gitignore_content

    assert (project_path / "views" / "html" / "index.html").exists()

    assert (project_path / ".ruff.toml").exists()


def test_wizard_minimal(temp_project_dir: Path) -> None:
    """
    Simulation test 'Minimalist':
    Simple + No DB + No Lint + No Views.

    Input Order:
    1. Name: 'mini_app'
    2. Arch: '1' (Simple)
    3. ORM: '3' (None)
    4. Lint: '3' (None)
    5. View: 'n'
    6. Test: 'n'
    """
    user_inputs = "mini_app\n1\n3\n3\nn\nn\n"
    result = runner.invoke(app, [], input=user_inputs)

    assert result.exit_code == 0
    project_path = temp_project_dir / "mini_app"

    _assert_common_files(project_path)

    assert not (project_path / "app").exists()
    assert not (project_path / "views").exists()
    assert not (project_path / "config").exists()
    assert not (project_path / ".env").exists()
    assert not (project_path / ".ruff.toml").exists()


def test_args_mode_defaults(temp_project_dir: Path) -> None:
    """
    Test old way: `fastapi-new projectname`.
    Should automatically use defaults (Simple, No DB, No Lint, No Views).
    """
    user_inputs = "\n\n\nn\ny\n" 

    result = runner.invoke(app, ["fast_project"], input=user_inputs)

    assert result.exit_code == 0
    project_path = temp_project_dir / "fast_project"
    
    _assert_common_files(project_path)
    assert not (project_path / "app").exists()


def test_rejects_existing_directory(temp_project_dir: Path) -> None:
    """Ensure the wizard rejects if the folder already exists."""
    (temp_project_dir / "duplicate").mkdir()

    user_inputs = "duplicate\n"
    result = runner.invoke(app, [], input=user_inputs)

    assert result.exit_code == 1
    assert "already exists" in result.output


def test_uv_missing_handler(temp_project_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Simulation if the user does not have 'uv' installed."""
    monkeypatch.setattr(shutil, "which", MagicMock(return_value=None))

    user_inputs = "no_uv_app\n"
    result = runner.invoke(app, [], input=user_inputs)

    assert result.exit_code == 1
    assert "uv is required" in result.output

    project_path = temp_project_dir / "no_uv_app"
    assert not project_path.exists()