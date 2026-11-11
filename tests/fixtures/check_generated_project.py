import sys
import sysconfig

from fastapi.testclient import TestClient
from main import app

expected_python = sys.argv[1]
python = f"{sys.version_info.major}.{sys.version_info.minor}"
if sysconfig.get_config_var("Py_GIL_DISABLED"):
    python += "t"
assert python == expected_python, f"Expected Python {expected_python}, got {python}"

with TestClient(app) as client:
    response = client.get("/")
assert response.status_code == 200
assert response.json() == {"message": "Hello World"}
