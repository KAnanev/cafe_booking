import asyncio
import os
import sys
from collections.abc import AsyncGenerator, Awaitable, Callable

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from core.config import Settings
from core.db import Base, get_async_session
from main import app
from models.user import User, UserRoles
from schemas.user import UserCreate

from .fixtures.test_data import DEFAULT_HASH, DEFAULT_PASSWORD

# --- Event loop policy for Windows (asyncpg compatibility) ---
if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@pytest.fixture(scope='session')
def test_settings() -> Settings:
    """Возвращает настройки приложения для тестового окружения."""
    return Settings(
        postgres_host=os.getenv('POSTGRES_HOST', 'localhost'),
        postgres_port=int(os.getenv('POSTGRES_PORT', '5432')),
        postgres_user=os.getenv('POSTGRES_USER', 'username'),
        postgres_password=os.getenv('POSTGRES_PASSWORD', 'password'),
        postgres_db='cafe_db',
        postgres_db_override='test_cafe_booking',
        secret='test-secret',
    )


@pytest_asyncio.fixture(scope='session')
async def test_engine(
    test_settings: Settings,
) -> AsyncGenerator[AsyncEngine, None]:
    """Создаёт асинхронный SQLAlchemy engine для тестовой БД.

    Таблицы создаются один раз перед запуском тестов
    и удаляются после завершения всей сессии.
    """
    engine = create_async_engine(
        test_settings.database_url,
        echo=False,
        poolclass=NullPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(
    test_engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """Предоставляет изолированную сессию БД для одного теста.

    После выполнения теста все изменения откатываются.
    """
    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.rollback()


@pytest_asyncio.fixture
async def create_user(
    db_session: AsyncSession,
) -> Callable[..., Awaitable[User]]:
    """Фабрика для создания пользователя напрямую в тестовой БД."""

    async def _create_user(
        *,
        email: str,
        phone: str,
        username: str,
        hashed_password: str = DEFAULT_HASH,
        role: UserRoles = UserRoles.USER,
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
    """Фабрика валидных данных UserCreate для API-тестов."""

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


@pytest_asyncio.fixture
async def async_client(
    test_engine: AsyncEngine,
) -> AsyncGenerator[AsyncClient, None]:
    """HTTP-клиент FastAPI с подменённой зависимостью БД."""
    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async def override_get_async_session() -> AsyncGenerator[
        AsyncSession,
        None,
    ]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_async_session] = override_get_async_session

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url='http://test',
    ) as client:
        yield client

    app.dependency_overrides.clear()
