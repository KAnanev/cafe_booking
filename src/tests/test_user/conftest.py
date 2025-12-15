import asyncio
import os
from asyncio import AbstractEventLoop
from collections.abc import AsyncGenerator, Awaitable, Callable, Generator
from typing import Any

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
from models.user import User, UserRoles
from schemas.user import UserCreate

from .fixtures.test_data import DEFAULT_HASH, DEFAULT_PASSWORD


@pytest.fixture(scope='session')
def test_settings() -> Settings:
    """Предоставляет настройки для тестового окружения.

    Подменяет имя базы данных на фиксированную тестовую БД 'test_cafe_booking',
    остальные параметры из переменных окружения или значений по умолчанию.
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
    """Создаёт асинхронный SQLAlchemy-движок для тестовой базы данных.

    Использует пул NullPool, чтобы избежать утечек соединений и конфликтов
    при параллельном или повторном запуске тестов.
    """
    return create_async_engine(
        test_settings.database_url,
        echo=False,
        poolclass=NullPool,
    )


@pytest_asyncio.fixture(scope='function')
async def db_session(
    test_engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """Предоставляет изолированную асинхронную сессию БД для каждого теста.

    Перед выполнением теста удаляет все таблицы и создаёт их заново,
    обеспечивая чистое состояние. После завершения теста сессия закрывается.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )

    async with session_factory() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope='session')
def event_loop() -> Generator[AbstractEventLoop, Any, None]:
    """Создаёт и управляет жизненным циклом event loop'а для pytest-asyncio.

    Обеспечивает стабильную работу асинхронных фикстур и тестов,
    изолируя их от глобального цикла событий.
    """
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def create_user(
    db_session: AsyncSession,
) -> Callable[..., Awaitable[User]]:
    """Фабрика для создания и сохранения пользователей в тестовой БД.

    Принимает email, телефон, имя пользователя и опциональные параметры
    (хеш пароля, роль). Возвращает сохранённый экземпляр модели User.
    Роль по умолчанию — UserRole.USER (значение 3).
    """

    async def _create_user(
        *,
        email: str,
        phone: str,
        username: str,
        hashed_password: str = DEFAULT_HASH,
        role: int = UserRoles.USER,
    ) -> User:
        user = User(
            email=email,
            phone=phone,
            username=username,
            hashed_password=hashed_password,
            role=role,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    return _create_user


@pytest.fixture
def user_create_data() -> Callable[..., UserCreate]:
    """Фабрика для создания валидных Pydantic-объектов UserCreate.

    Используется для имитации входных данных от API (регистрация).
    Пароль по умолчанию — 'secret', остальные поля задаются явно.
    """

    def _user_create(
        *,
        email: str,
        phone: str,
        username: str,
        password: str = DEFAULT_PASSWORD,
    ) -> UserCreate:
        return UserCreate(
            email=email,
            phone=phone,
            username=username,
            password=password,
        )

    return _user_create
