from datetime import datetime, timezone

from sqlalchemy import DateTime, MetaData, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from ulid import ULID

# Predictable names for indexes and constraints, so migrations can find
# and change them later (SQLite and PostgreSQL both need this)
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


def utc_now() -> datetime:
    """Current time in UTC. Every timestamp in the app uses this."""
    return datetime.now(timezone.utc)


def new_id() -> str:
    """A new ULID: globally unique, URL-safe and sortable by creation time."""
    return str(ULID())


class Base(DeclarativeBase):
    """Parent class for every database model."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class IdMixin:
    """Adds a ULID primary key."""

    id: Mapped[str] = mapped_column(
        String(26), primary_key=True, default=new_id, sort_order=-10
    )


class TimestampMixin:
    """Adds created_at and updated_at, both in UTC."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=func.now(),
        nullable=False,
        sort_order=100,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        server_default=func.now(),
        nullable=False,
        sort_order=100,
    )


class SoftDeleteMixin:
    """Adds deleted_at. NULL means active; a timestamp means deleted, and when."""

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None, sort_order=100
    )