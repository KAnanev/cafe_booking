from celery import Celery

from core.config import settings

celery_app = Celery(
    'booking',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_BACKEND,
    include=['tasks.outbox'],
)

celery_app.conf.update(
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
)


celery_app.conf.beat_schedule = {
    'dispatch-outbox-every-30s': {
        'task': 'tasks.outbox.dispatch_outbox',
        'schedule': 30.0,
        'args': (100,),
    },
}
