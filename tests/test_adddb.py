"""
Tests for add-db command.
"""

import pytest
from pathlib import Path
from typing import Any

from typer.testing import CliRunner

from fastapi_new.cli import app
from fastapi_new.adddb import (
    SUPPORTED_ENGINES,
    find_project_root,
    update_config_engine,
    update_env_file,
)

runner = CliRunner()


@pytest.fixture
def project_structure(tmp_path: Path) -> Path:
    """Create a minimal FastAPI-New project structure."""
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    (app_dir / "core").mkdir()

    # Create config.py
    config_content = '''"""
Config Module
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_ENGINE: str = "sqlite"
    DATABASE_URL: str = "sqlite:///./app.db"


settings = Settings()
'''
    (app_dir / "core" / "config.py").write_text(config_content)

    return tmp_path


@pytest.fixture
def temp_project_dir(project_structure: Path, monkeypatch: Any) -> Path:
    """Create a temporary project directory and cd into it."""
    monkeypatch.chdir(project_structure)
    return project_structure


class TestSupportedEngines:
    """Tests for SUPPORTED_ENGINES configuration."""

    def test_postgres_is_supported(self) -> None:
        assert "postgres" in SUPPORTED_ENGINES
        assert "PostgreSQL" in SUPPORTED_ENGINES["postgres"]["name"]
        assert "asyncpg" in SUPPORTED_ENGINES["postgres"]["dependencies"]

    def test_mysql_is_supported(self) -> None:
        assert "mysql" in SUPPORTED_ENGINES
        assert "MySQL" in SUPPORTED_ENGINES["mysql"]["name"]
        assert "aiomysql" in SUPPORTED_ENGINES["mysql"]["dependencies"]

    def test_sqlite_is_supported(self) -> None:
        assert "sqlite" in SUPPORTED_ENGINES
        assert "SQLite" in SUPPORTED_ENGINES["sqlite"]["name"]
        assert "aiosqlite" in SUPPORTED_ENGINES["sqlite"]["dependencies"]

    def test_mongodb_is_supported(self) -> None:
        assert "mongodb" in SUPPORTED_ENGINES
        assert "MongoDB" in SUPPORTED_ENGINES["mongodb"]["name"]
        assert "motor" in SUPPORTED_ENGINES["mongodb"]["dependencies"]

    def test_all_engines_have_required_fields(self) -> None:
        required_fields = ["name", "dependencies", "url_example"]
        for engine, config in SUPPORTED_ENGINES.items():
            for field in required_fields:
                assert field in config, f"{engine} missing {field}"


class TestFindProjectRoot:
    """Tests for find_project_root function."""

    def test_finds_root_in_current_directory(self, tmp_path: Path, monkeypatch: Any) -> None:
        (tmp_path / "app").mkdir()
        monkeypatch.chdir(tmp_path)

        result = find_project_root()
        assert result == tmp_path

    def test_returns_none_when_no_project(self, tmp_path: Path, monkeypatch: Any) -> None:
        monkeypatch.chdir(tmp_path)

        result = find_project_root()
        assert result is None


class TestUpdateConfigEngine:
    """Tests for update_config_engine function."""

    def test_updates_database_engine(self, tmp_path: Path) -> None:
        config = tmp_path / "config.py"
        config.write_text('DATABASE_ENGINE: str = "sqlite"')

        result = update_config_engine(config, "postgres")

        assert result is True
        content = config.read_text()
        assert '"postgres"' in content
        assert '"sqlite"' not in content

    def test_updates_with_different_quote_styles(self, tmp_path: Path) -> None:
        config = tmp_path / "config.py"
        config.write_text("DATABASE_ENGINE: str = 'sqlite'")

        result = update_config_engine(config, "mysql")

        assert result is True
        content = config.read_text()
        assert '"mysql"' in content

    def test_handles_spaces_around_equals(self, tmp_path: Path) -> None:
        config = tmp_path / "config.py"
        config.write_text('DATABASE_ENGINE : str  =  "sqlite"')

        result = update_config_engine(config, "postgres")

        assert result is True
        content = config.read_text()
        assert '"postgres"' in content

    def test_returns_false_for_missing_file(self, tmp_path: Path) -> None:
        config = tmp_path / "nonexistent.py"

        result = update_config_engine(config, "postgres")

        assert result is False

    def test_returns_false_when_no_match(self, tmp_path: Path) -> None:
        config = tmp_path / "config.py"
        config.write_text("OTHER_SETTING = 'value'")

        result = update_config_engine(config, "postgres")

        assert result is False


class TestUpdateEnvFile:
    """Tests for update_env_file function."""

    def test_creates_env_file_if_not_exists(self, tmp_path: Path) -> None:
        env_file = tmp_path / ".env"

        result = update_env_file(env_file, "postgres", "postgresql://...")

        assert result is True
        assert env_file.exists()
        content = env_file.read_text()
        assert "DATABASE_ENGINE=postgres" in content

    def test_updates_existing_database_engine(self, tmp_path: Path) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text("DATABASE_ENGINE=sqlite\nOTHER=value")

        result = update_env_file(env_file, "postgres", "postgresql://...")

        assert result is True
        content = env_file.read_text()
        assert "DATABASE_ENGINE=postgres" in content
        assert "DATABASE_ENGINE=sqlite" not in content
        assert "OTHER=value" in content

    def test_copies_from_env_example(self, tmp_path: Path) -> None:
        env_example = tmp_path / ".env.example"
        env_example.write_text("DATABASE_ENGINE=sqlite\nSECRET_KEY=xxx")

        env_file = tmp_path / ".env"

        result = update_env_file(env_file, "mysql", "mysql://...")

        assert result is True
        content = env_file.read_text()
        assert "DATABASE_ENGINE=mysql" in content
        assert "SECRET_KEY=xxx" in content

    def test_updates_database_url_for_sqlite(self, tmp_path: Path) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text("DATABASE_ENGINE=postgres\nDATABASE_URL=postgresql://old")

        result = update_env_file(env_file, "sqlite", "sqlite:///./app.db")

        assert result is True
        content = env_file.read_text()
        assert "DATABASE_ENGINE=sqlite" in content
        assert "sqlite:///./app.db" in content


class TestAddDbCommand:
    """Tests for add-db CLI command."""

    def test_adds_postgres_successfully(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["add-db", "postgres"])

        assert result.exit_code == 0
        assert "Success!" in result.output or "PostgreSQL" in result.output

    def test_adds_mysql_successfully(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["add-db", "mysql"])

        assert result.exit_code == 0
        assert "MySQL" in result.output

    def test_adds_sqlite_successfully(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["add-db", "sqlite"])

        assert result.exit_code == 0
        assert "SQLite" in result.output

    def test_adds_mongodb_successfully(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["add-db", "mongodb"])

        assert result.exit_code == 0
        assert "MongoDB" in result.output

    def test_accepts_postgresql_alias(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["add-db", "postgresql"])

        assert result.exit_code == 0
        assert "PostgreSQL" in result.output

    def test_accepts_mongo_alias(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["add-db", "mongo"])

        assert result.exit_code == 0
        assert "MongoDB" in result.output

    def test_case_insensitive_engine_name(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["add-db", "POSTGRES"])

        assert result.exit_code == 0
        assert "PostgreSQL" in result.output

    def test_fails_for_unknown_engine(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["add-db", "oracle"])

        assert result.exit_code == 1
        assert "Unknown database engine" in result.output
        assert "oracle" in result.output

    def test_shows_supported_engines_on_error(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["add-db", "unknown"])

        assert result.exit_code == 1
        assert "Supported engines" in result.output
        assert "postgres" in result.output
        assert "mysql" in result.output

    def test_fails_outside_project(self, tmp_path: Path, monkeypatch: Any) -> None:
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["add-db", "postgres"])

        assert result.exit_code == 1
        assert "Could not find project root" in result.output

    def test_updates_config_file(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["add-db", "postgres"])

        assert result.exit_code == 0

        config = temp_project_dir / "app" / "core" / "config.py"
        content = config.read_text()
        assert '"postgres"' in content

    def test_creates_env_file(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["add-db", "postgres"])

        assert result.exit_code == 0

        env_file = temp_project_dir / ".env"
        assert env_file.exists()
        content = env_file.read_text()
        assert "DATABASE_ENGINE=postgres" in content

    def test_shows_configuration_info(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["add-db", "postgres"])

        assert result.exit_code == 0
        assert "Configuration" in result.output or "DATABASE_ENGINE" in result.output
        assert "postgres" in result.output

    def test_shows_dependency_install_command(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["add-db", "postgres"])

        assert result.exit_code == 0
        assert "uv add" in result.output or "dependencies" in result.output.lower()

    def test_shows_url_example(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["add-db", "postgres"])

        assert result.exit_code == 0
        assert "DATABASE_URL" in result.output
        assert "postgresql://" in result.output


class TestAddDbWithInstallFlag:
    """Tests for add-db command with --install flag."""

    def test_install_flag_exists(self, temp_project_dir: Path, monkeypatch: Any) -> None:
        # Mock subprocess to avoid actually installing
        import subprocess

        calls = []

        def mock_run(*args: Any, **kwargs: Any) -> Any:
            calls.append(args)
            result = type("Result", (), {"returncode": 0})()
            return result

        monkeypatch.setattr(subprocess, "run", mock_run)

        result = runner.invoke(app, ["add-db", "postgres", "--install"])

        # Should attempt to install dependencies
        assert result.exit_code == 0 or "uv" in result.output.lower()

    def test_short_install_flag(self, temp_project_dir: Path, monkeypatch: Any) -> None:
        import subprocess

        def mock_run(*args: Any, **kwargs: Any) -> Any:
            result = type("Result", (), {"returncode": 0})()
            return result

        monkeypatch.setattr(subprocess, "run", mock_run)

        result = runner.invoke(app, ["add-db", "postgres", "-i"])

        assert result.exit_code == 0


class TestAddDbEngineSpecific:
    """Tests for engine-specific behavior."""

    def test_postgres_shows_correct_url_format(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["add-db", "postgres"])

        assert "postgresql://" in result.output

    def test_mysql_shows_correct_url_format(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["add-db", "mysql"])

        assert "mysql://" in result.output

    def test_sqlite_shows_correct_url_format(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["add-db", "sqlite"])

        assert "sqlite:///" in result.output

    def test_mongodb_shows_correct_url_format(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["add-db", "mongodb"])

        assert "mongodb://" in result.output

    def test_postgres_mentions_asyncpg(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["add-db", "postgres"])

        # Should mention asyncpg in dependencies
        assert "asyncpg" in result.output or "psycopg" in result.output

    def test_mysql_mentions_aiomysql(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["add-db", "mysql"])

        assert "aiomysql" in result.output or "pymysql" in result.output

    def test_mongodb_mentions_motor(self, temp_project_dir: Path) -> None:
        result = runner.invoke(app, ["add-db", "mongodb"])

        assert "motor" in result.output or "pymongo" in result.output
