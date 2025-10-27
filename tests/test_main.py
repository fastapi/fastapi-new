from fastapi_new import __version__


def test_version_var_exists() -> None:
    assert isinstance(__version__, str)
