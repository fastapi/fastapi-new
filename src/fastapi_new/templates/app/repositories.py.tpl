"""
{{app_name_pascal}} Repositories
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.apps.{{app_name}}.models import {{model_name}}


class {{model_name}}Repository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # Add your repository methods here
