import uuid
from typing import AsyncGenerator

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base, declared_attr, sessionmaker

from core.config import settings


class PreBase:
    """Базовый класс для моделей SQLAlchemy."""

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    @declared_attr
    def __tablename__(self) -> str:
        return self.__name__.lower()


Base = declarative_base(cls=PreBase)
engine: AsyncEngine = create_async_engine(settings.database_url)

AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Возвращает асинхронную сессию SQLAlchemy."""
    async with AsyncSessionLocal() as async_session:
        yield async_session
