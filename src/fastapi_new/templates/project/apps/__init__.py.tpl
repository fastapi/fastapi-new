"""
Apps Module
Contains all application modules (MSSR pattern).

Each app follows the Model-Schema-Service-Repository pattern:
    app/apps/your_app/
    ├── __init__.py
    ├── models.py       # SQLAlchemy ORM models
    ├── schemas.py      # Pydantic request/response schemas
    ├── services.py     # Business logic
    ├── repositories.py # Data access layer
    ├── routes.py       # API endpoints
    └── dependencies.py # FastAPI dependencies

Create a new app using:
    fastapi-new createapp <app_name>
"""
