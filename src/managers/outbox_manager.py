import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models import OutboxMessage, OutboxStatus


def utcnow() -> datetime:
    """Текущее время."""
    return datetime.now(timezone.utc)


class OutboxManager:
    """Менеджер сообщений."""

    def __init__(self, session: AsyncSession) -> None:
        """Инициализирует менеджер сессией базы данных."""
        self.session = session

    async def add(
        self,
        *,
        event_type: str,
        aggregate_type: str,
        aggregate_id: uuid.UUID,
        payload: dict[str, Any],
        available_at: datetime,
    ) -> OutboxMessage:
        """Создаёт запись OutboxMessage."""
        msg = OutboxMessage(
            event_type=event_type,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            payload=payload,
            available_at=available_at,
        )
        self.session.add(msg)
        return msg

    async def fetch_ready_for_dispatch(
        self,
        *,
        limit: int = 100,
    ) -> list[OutboxMessage]:
        """Выбирает сообщения, которые можно ставить в очередь на отправку."""
        stmt = (
            select(OutboxMessage)
            .where(
                OutboxMessage.status == OutboxStatus.PENDING,
                OutboxMessage.available_at <= utcnow(),
            )
            .order_by(OutboxMessage.available_at.asc())
            .with_for_update(of=OutboxMessage, skip_locked=True)
            .limit(limit)
        )

        messages = list((await self.session.execute(stmt)).scalars().all())

        now = utcnow()

        for message in messages:
            message.status = OutboxStatus.ENQUEUED
            message.locked_at = now

        return messages

    async def mark_sent(self, *, outbox_id: uuid.UUID) -> None:
        """Отмечает сообщение отправленным."""
        stmt = (
            update(OutboxMessage)
            .where(OutboxMessage.id == outbox_id)
            .values(
                status=OutboxStatus.SENT,
                sent_at=utcnow(),
                last_error=None,
            )
        )
        await self.session.execute(stmt)

    async def mark_failed(self, *, outbox_id: uuid.UUID, error: str) -> None:
        """Отмечает сообщение неудачным."""
        stmt = (
            update(OutboxMessage)
            .where(OutboxMessage.id == outbox_id)
            .values(
                status=OutboxStatus.FAILED,
                last_error=error[:2000],
                attempts=OutboxMessage.attempts + 1,
            )
        )
        await self.session.execute(stmt)

    async def cancel_reminder_for_booking(
        self,
        *,
        booking_id: uuid.UUID,
    ) -> None:
        """Отменяет будущие напоминания."""
        stmt = (
            update(OutboxMessage)
            .where(
                OutboxMessage.aggregate_type == 'booking',
                OutboxMessage.aggregate_id == booking_id,
                OutboxMessage.event_type == 'booking.reminder.user',
                OutboxMessage.status.in_([
                    OutboxStatus.PENDING,
                    OutboxStatus.ENQUEUED,
                ]),
            )
            .values(
                status=OutboxStatus.CANCELED,
            )
        )
        await self.session.execute(stmt)
