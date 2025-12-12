import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID


def utcnow() -> datetime:
    """Возвращает текущее время в UTC."""
    return datetime.now(timezone.utc)


class UUIDMixin:
    """Миксин для ID."""

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )


class TimestampMixin:
    """Миксин для временных меток."""

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
        server_default=func.now(),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
        server_default=func.now(),
        onupdate=func.now(),
    )


class ActiveMixin:
    """Миксин для active."""

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default='true',
    )
