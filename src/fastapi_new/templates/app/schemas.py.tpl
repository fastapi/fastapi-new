"""
{{app_name_pascal}} Schemas
"""

from pydantic import BaseModel


class {{model_name}}Base(BaseModel):
    # Add your base fields here
    pass


class {{model_name}}Create({{model_name}}Base):
    # Add fields required for creation
    pass


class {{model_name}}Update(BaseModel):
    # Add fields for update (all optional)
    pass


class {{model_name}}Response({{model_name}}Base):
    id: int

    class Config:
        from_attributes = True
