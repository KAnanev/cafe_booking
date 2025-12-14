from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, func, text


def utcnow() -> datetime:
    """Возвращает текущее время в UTC."""
    return datetime.now(timezone.utc)


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
        server_default=text('true'),
    )
