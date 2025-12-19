from fastapi_new import __version__


def test_version_variable_exists() -> None:
    assert isinstance(__version__, str)