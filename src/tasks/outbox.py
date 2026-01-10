import asyncio
import logging
import uuid

from celery import shared_task

from core.db_celery import CelerySessionLocal
from managers.outbox_manager import OutboxManager
from models import OutboxMessage, OutboxStatus
from tasks.notifications import dispatch_outbox_event

logger = logging.getLogger(__name__)


@shared_task(name='tasks.outbox.dispatch_outbox')
def dispatch_outbox(limit: int = 100) -> int:
    """Периодически забирает готовые PENDING и ставит задачи на отправку."""
    return asyncio.run(_dispatch_outbox(limit))


async def _dispatch_outbox(limit: int) -> int:
    async with CelerySessionLocal() as session:
        manager = OutboxManager(session)

        async with session.begin():
            messages = await manager.fetch_ready_for_dispatch(limit=limit)

        for msg in messages:
            send_outbox_message.delay(str(msg.id))

        return len(messages)


@shared_task(
    name='tasks.outbox.send_outbox_message',
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=5,
)
def send_outbox_message(outbox_id: str) -> str:
    """Отправляет одно outbox-сообщение."""
    return asyncio.run(_send_outbox_message(outbox_id))


async def _send_outbox_message(outbox_id: str) -> str:
    outbox_uuid = uuid.UUID(outbox_id)

    async with CelerySessionLocal() as session:
        manager = OutboxManager(session)

        msg = await session.get(OutboxMessage, outbox_uuid)
        if not msg:
            return 'not_found'

        if msg.status in (OutboxStatus.SENT, OutboxStatus.CANCELED):
            return f'skipped:{msg.status}'

        try:
            await dispatch_outbox_event(msg.event_type, msg.payload)

            async with session.begin():
                await manager.mark_sent(outbox_id=msg.id)

            return 'sent'

        except Exception as e:
            logger.exception('Outbox send failed: %s', e)

            async with session.begin():
                await manager.mark_failed(outbox_id=msg.id, error=str(e))

            raise
