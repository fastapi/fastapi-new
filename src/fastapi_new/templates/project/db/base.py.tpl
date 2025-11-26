"""
Database base models - For ORM usage (optional).

If you're using an ORM like SQLAlchemy or Tortoise:

SQLAlchemy example:
    from sqlalchemy.ext.declarative import declarative_base
    
    Base = declarative_base()
    
    # Then in your models:
    class User(Base):
        __tablename__ = "users"
        id = Column(Integer, primary_key=True)

Tortoise ORM example:
    from tortoise import Model, fields
    
    class User(Model):
        id = fields.IntField(pk=True)
        name = fields.CharField(max_length=255)

If you're not using an ORM, you can delete this file.
"""

# Your ORM base class goes here (if needed)
