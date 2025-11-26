"""
{{app_name_pascal}} Dependencies
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_db


# Add your dependencies here
