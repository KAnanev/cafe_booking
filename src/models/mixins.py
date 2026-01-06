from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, func, text
from sqlalchemy.orm import Mapped, mapped_column


def utcnow() -> datetime:
    """Возвращает текущее время в UTC."""
    return datetime.now(timezone.utc)


class TimestampMixin:
    """Миксин для временных меток."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
        server_default=func.now(),
        onupdate=func.now(),
    )


class ActiveMixin:
    """Миксин для active."""

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text('true'),
    )
