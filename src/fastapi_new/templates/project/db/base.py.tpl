"""
Database Base Model
SQLAlchemy declarative base and common model utilities.
"""

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, MetaData, func
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


# Naming convention for constraints (helps with migrations)
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """
    Base class for all database models.

    All models should inherit from this class:

        from app.db.base import Base

        class User(Base):
            __tablename__ = "users"

            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str] = mapped_column(String(100))
    """

    metadata = MetaData(naming_convention=convention)

    # Generate __tablename__ automatically from class name
    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Generate table name from class name (snake_case)."""
        name = cls.__name__
        # Convert CamelCase to snake_case
        result = [name[0].lower()]
        for char in name[1:]:
            if char.isupper():
                result.append("_")
                result.append(char.lower())
            else:
                result.append(char)
        return "".join(result) + "s"


class TimestampMixin:
    """
    Mixin to add created_at and updated_at timestamps to models.

    Usage:
        class User(Base, TimestampMixin):
            __tablename__ = "users"
            id: Mapped[int] = mapped_column(primary_key=True)
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class SoftDeleteMixin:
    """
    Mixin to add soft delete functionality to models.

    Usage:
        class User(Base, SoftDeleteMixin):
            __tablename__ = "users"
            id: Mapped[int] = mapped_column(primary_key=True)
    """

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=None,
        nullable=True,
    )

    is_deleted: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )

    def soft_delete(self) -> None:
        """Mark the record as deleted."""
        self.deleted_at = datetime.now(timezone.utc)
        self.is_deleted = True

    def restore(self) -> None:
        """Restore a soft-deleted record."""
        self.deleted_at = None
        self.is_deleted = False


class BaseModel(Base, TimestampMixin):
    """
    Base model with common fields.
    Includes automatic timestamps.

    Usage:
        class User(BaseModel):
            __tablename__ = "users"

            id: Mapped[int] = mapped_column(primary_key=True)
            email: Mapped[str] = mapped_column(String(255), unique=True)
    """

    __abstract__ = True

    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    def update(self, **kwargs: Any) -> None:
        """Update model attributes from kwargs."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def __repr__(self) -> str:
        """String representation of the model."""
        class_name = self.__class__.__name__
        attrs = ", ".join(
            f"{col.name}={getattr(self, col.name)!r}"
            for col in self.__table__.columns
            if col.primary_key
        )
        return f"<{class_name}({attrs})>"
