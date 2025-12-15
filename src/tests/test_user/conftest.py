import asyncio
import os
import sys
import uuid
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
from core.security import create_access_token
from main import app
from models.user import User, UserRoles
from schemas.user import UserCreate

from .fixtures.test_data import (
    DEFAULT_HASH,
    DEFAULT_PASSWORD,
)

# ---------------------------------------------------------------------
# Event loop policy (Windows)
# ---------------------------------------------------------------------

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


# ---------------------------------------------------------------------
# Test settings & database
# ---------------------------------------------------------------------


@pytest.fixture(scope='session')
def test_settings() -> Settings:
    """Настройки приложения для тестового окружения."""
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
    """Асинхронный engine для тестовой БД."""
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
    """Изолированная сессия БД для одного теста."""
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


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------


def make_token(user_id: str) -> str:
    """Создаёт JWT access-токен для пользователя."""
    return create_access_token(user_id)


# ---------------------------------------------------------------------
# Factories
# ---------------------------------------------------------------------


@pytest_asyncio.fixture
async def create_user(
    db_session: AsyncSession,
) -> Callable[..., Awaitable[User]]:
    """Фабрика создания пользователя напрямую в БД."""

    async def _create_user(
        *,
        username: str,
        hashed_password: str = DEFAULT_HASH,
        role: UserRoles = UserRoles.USER,
    ) -> User:
        suffix = str(uuid.uuid4().int)[:7]
        user = User(
            email=f'{username}_{suffix}@example.ru',
            phone=f'+7999{suffix}',
            username=f'{username}_{suffix}',
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
    """Фабрика валидных данных UserCreate."""

    def _user_create(
        *,
        email: str | None = None,
        phone: str | None = None,
        username: str,
        hashed_password: str = DEFAULT_HASH,
    ) -> UserCreate:
        suffix = str(uuid.uuid4().int)[:7]

        if not email:
            email = f'{username}_{suffix}@example.ru'

        if not phone:
            phone = f'+7999{suffix}'

        return UserCreate(
            email=email,
            phone=phone,
            username=f'{username}_{suffix}',
            password=hashed_password,
        )

    return _user_create


# ---------------------------------------------------------------------
# HTTP client
# ---------------------------------------------------------------------


@pytest_asyncio.fixture
async def async_client(
    test_engine: AsyncEngine,
) -> AsyncGenerator[AsyncClient, None]:
    """HTTP-клиент FastAPI с подменённой БД."""
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


# ---------------------------------------------------------------------
# Users & tokens
# ---------------------------------------------------------------------


@pytest_asyncio.fixture
async def regular_user(create_user: Callable) -> User:
    """Пользователь с ролью USER."""
    return await create_user(
        username='user',
        role=UserRoles.USER,
    )


@pytest_asyncio.fixture
async def admin_user(create_user: Callable) -> User:
    """Пользователь с ролью ADMIN."""
    return await create_user(
        username='admin',
        role=UserRoles.ADMIN,
    )


@pytest_asyncio.fixture
async def manager_user(create_user: Callable) -> User:
    """Пользователь с ролью MANAGER."""
    return await create_user(
        username='manager',
        role=UserRoles.MANAGER,
    )


@pytest.fixture
def user_token(regular_user: User) -> str:
    """Токен пользователя USER."""
    return make_token(str(regular_user.id))


@pytest.fixture
def admin_token(admin_user: User) -> str:
    """Токен пользователя ADMIN."""
    return make_token(str(admin_user.id))


@pytest.fixture
def manager_token(manager_user: User) -> str:
    """Токен пользователя MANAGER."""
    return make_token(str(manager_user.id))


# ---------------------------------------------------------------------
# Payloads
# ---------------------------------------------------------------------


@pytest.fixture
def new_user_payload(user_create_data: Callable) -> UserCreate:
    """Валидные и уникальные данные нового пользователя."""
    suffix = str(uuid.uuid4().int)[:7]
    return user_create_data(
        email=f'new_user_{suffix}@example.ru',
        phone=f'+7999{suffix}',
        username=f'new_user_{suffix}',
        hashed_password=DEFAULT_PASSWORD,
    )
