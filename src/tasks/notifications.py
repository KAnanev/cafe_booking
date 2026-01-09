import logging
from typing import Any

logger = logging.getLogger(__name__)


async def dispatch_outbox_event(
    event_type: str,
    payload: dict[str, Any],
) -> None:
    """Напоминание."""
    if event_type.startswith('booking.notify.admin'):
        await notify_admin(event_type, payload)
        return

    if event_type == 'booking.reminder.user':
        await remind_user(payload)
        return

    raise ValueError(f'Unknown outbox event_type: {event_type}')


async def notify_admin(event_type: str, payload: dict[str, Any]) -> None:
    """Напоминание админу."""
    logger.info('[ADMIN NOTIFY] %s payload=%s', event_type, payload)


async def remind_user(payload: dict[str, Any]) -> None:
    """Напоминание пользователю."""
    logger.info('[USER REMINDER] payload=%s', payload)
