from textwrap import dedent

TEMPLATE_DB_CONNECTION = dedent("""
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
import os

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(str(DATABASE_URL), echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
""").strip()

TEMPLATE_ENV = """
# Option 1: SQLite (Default - No setup required)
# DATABASE_URL=sqlite:///./{project_name}.db

# Option 2: MySQL (Requires: uv add pymysql)
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/{project_name}

# Option 3: PostgreSQL (Requires: uv add psycopg2-binary)
# DATABASE_URL=postgresql://postgres:password@localhost:5432/{project_name}
"""

TEMPLATE_MAIN = dedent("""
from fastapi import FastAPI
# from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Mount static files (if views folder exists)
# app.mount("/static", StaticFiles(directory="views/css"), name="static")

@app.get("/")
def main():
    return {"message": "Welcome to your FastAPI project!"}
""").strip()

TEMPLATE_HTML = dedent("""
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FastAPI View</title>
        <link rel="stylesheet" href="/static/css/style.css">
    </head>
    <body>
        <h1>Hello from FastAPI Views! 🚀</h1>
        <script src="/static/js/main.js"></script>
    </body>
</html>
""").strip()

TEMPLATE_CSS = dedent("""
body {
    font-family: sans-serif;
    background-color: #f0fdf4; /* Green-50 */
    color: #166534; /* Green-800 */
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    margin: 0;
}
""").strip()

TEMPLATE_JS = dedent("""
console.log("FastAPI Views are active!");
""").strip()

TEMPLATE_GITIGNORE = dedent("""
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Distribution / packaging
build/
dist/
*.egg-info/
*.egg
                            
# Environment variables
.env

# Testing / coverage
htmlcov/
.coverage
.coverage.*
coverage/
.pytest_cache/
tox/

# Type checking
.mypy_cache/

# Virtual environments
.venv
venv/

# IDE
.idea/

# OS
.DS_Store
Thumbs.db
""").strip()

TEMPLATE_RUFF = dedent("""
# .ruff.toml - Standalone configuration
line-length = 88
target-version = "py310"

[lint]
select = ["E", "F", "I"]
ignore = []
""").strip()

TEMPLATE_TESTING = dedent("""
def test_example():
    assert True
""").strip()