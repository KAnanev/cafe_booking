"""Фабрика сессий DB для обработчиков celery."""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from core.config import settings

celery_engine = create_async_engine(
    settings.database_url,
    echo=False,
    poolclass=NullPool,
)

CelerySessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    celery_engine,
    expire_on_commit=False,
)
