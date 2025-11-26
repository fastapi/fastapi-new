"""
{{app_name_pascal}} Models
"""

from sqlalchemy import Column, Integer, String
from app.db.base import Base


class {{model_name}}(Base):
    __tablename__ = "{{table_name}}"

    id = Column(Integer, primary_key=True, index=True)
    # Add your model fields here
