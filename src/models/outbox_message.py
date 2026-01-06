import enum
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Enum, Index, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.db import Base


class OutboxStatus(enum.StrEnum):
    """Статусы сообщений."""

    PENDING = 'PENDING'
    ENQUEUED = 'ENQUEUED'
    SENT = 'SENT'
    FAILED = 'FAILED'
    CANCELED = 'CANCELED'


class OutboxMessage(Base):
    """Модель сообщений."""

    event_type: Mapped[str] = mapped_column(String, nullable=False)
    aggregate_type: Mapped[str] = mapped_column(String, nullable=False)
    aggregate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)

    available_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    status: Mapped[OutboxStatus] = mapped_column(
        Enum(OutboxStatus, name='outbox_status'),
        nullable=False,
        server_default=text(f"'{OutboxStatus.PENDING.value}'"),
    )

    attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default='0',
    )

    locked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index('ix_outbox_status_available_at', 'status', 'available_at'),
        Index('ix_outbox_aggregate_type_id', 'aggregate_type', 'aggregate_id'),
    )
