"""Import every model here so Alembic can see all tables."""

from app.models.user import User

__all__ = ["User"]