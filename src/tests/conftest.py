import asyncio
import os
from asyncio import AbstractEventLoop
from typing import Any, AsyncGenerator, Generator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from core.config import Settings
from core.db import Base


@pytest.fixture(scope='session')
def test_settings() -> Settings:
    """Возвращает тестовые настройки приложения.

    Использует переменные окружения или значения по умолчанию
    для подключения к БД.
    Имя тестовой базы данных фиксировано: 'test_cafe_booking'.
    """
    return Settings(
        postgres_host=os.getenv('POSTGRES_HOST', 'localhost'),
        postgres_port=int(os.getenv('POSTGRES_PORT', '5432')),
        postgres_user=os.getenv('POSTGRES_USER', 'username'),
        postgres_password=os.getenv('POSTGRES_PASSWORD', 'password'),
        postgres_db='cafe_db',
        postgres_db_override='test_cafe_booking',
        secret='test-secret',
    )


@pytest.fixture(scope='session')
def test_engine(test_settings: Settings) -> AsyncEngine:
    """Создаёт асинхронный движок SQLAlchemy для тестовой базы данных.

    Использует NullPool, чтобы избежать проблем с подключениями в тестах.
    """
    return create_async_engine(
        test_settings.database_url,
        echo=False,
        poolclass=NullPool,
    )


@pytest_asyncio.fixture(scope='function')
async def db_session(
    test_engine: AsyncEngine,
    test_settings: Settings,
) -> AsyncGenerator[AsyncSession, None]:
    """Фикстура для создания изолированной сессии базы данных на каждый тест.

    Перед каждым тестом удаляет и заново создаёт все таблицы.
    После теста сессия автоматически закрывается.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session


# Переопределяем event_loop для pytest-asyncio
@pytest.fixture(scope='session')
def event_loop() -> Generator[AbstractEventLoop, Any, None]:
    """Заменяет стандартный event loop pytest на новый.

    Чтобы избежать конфликтов при использовании асинхронных фикстур.
    """
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
