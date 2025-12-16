import uuid

import pytest
from _pytest.monkeypatch import MonkeyPatch
from sqlalchemy.ext.asyncio import AsyncSession

from core.init_db import create_first_superuser
from crud.user import user_crud
from models.user import User, UserRoles


@pytest.mark.asyncio
async def test_create_first_superuser_creates_user(
    db_session: AsyncSession,
    monkeypatch: MonkeyPatch,
) -> None:
    """Создает суперпользователя."""
    monkeypatch.setattr(
        'core.init_db.settings.first_superuser_email',
        'admin@test.com',
    )
    monkeypatch.setattr(
        'core.init_db.settings.first_superuser_password',
        'super_secret',
    )

    await create_first_superuser(db_session)

    user = await user_crud.get_by_email(
        email='admin@test.com',
        session=db_session,
    )

    assert user is not None
    assert user.email == 'admin@test.com'
    assert user.role == UserRoles.ADMIN
    assert user.is_active is True
    assert user.is_superuser is True


@pytest.mark.asyncio
async def test_create_first_superuser_is_idempotent(
    db_session: AsyncSession,
    monkeypatch: MonkeyPatch,
) -> None:
    """Повторный тест не создает дубликат."""
    monkeypatch.setattr(
        'core.init_db.settings.first_superuser_email',
        'admin@test.com',
    )
    monkeypatch.setattr(
        'core.init_db.settings.first_superuser_password',
        'super_secret',
    )

    await create_first_superuser(db_session)
    user1 = await user_crud.get_by_email(
        email='admin@test.com',
        session=db_session,
    )

    await create_first_superuser(db_session)
    user2 = await user_crud.get_by_email(
        email='admin@test.com',
        session=db_session,
    )

    assert user1 is not None
    assert user2 is not None
    assert user1.id == user2.id


@pytest.mark.asyncio
async def test_create_first_superuser_skips_if_email_not_set(
    db_session: AsyncSession,
    monkeypatch: MonkeyPatch,
) -> None:
    """Приложение может стартовать без суперпользователя."""
    monkeypatch.setattr(
        'core.init_db.settings.first_superuser_email',
        None,
    )
    monkeypatch.setattr(
        'core.init_db.settings.first_superuser_password',
        'whatever',
    )

    await create_first_superuser(db_session)

    user = await user_crud.get_by_email(
        email='',
        session=db_session,
    )

    assert user is None


@pytest.mark.asyncio
async def test_create_first_superuser_does_not_override_existing_user(
    db_session: AsyncSession,
    monkeypatch: MonkeyPatch,
) -> None:
    """Не перезаписывается superuser."""
    email = f'admin_{uuid.uuid4().hex}@test.com'

    monkeypatch.setattr(
        'core.init_db.settings.first_superuser_email',
        email,
    )
    monkeypatch.setattr(
        'core.init_db.settings.first_superuser_password',
        'super_secret',
    )

    existing_user = User(
        username='existing_admin',
        email=email,
        phone='+79991234567',
        hashed_password='fake_hash',
        role=UserRoles.USER,
        is_active=True,
        is_superuser=False,
    )
    db_session.add(existing_user)
    await db_session.commit()
    await db_session.refresh(existing_user)

    await create_first_superuser(db_session)

    user = await user_crud.get_by_email(
        email=email,
        session=db_session,
    )

    assert user.id == existing_user.id
    assert user.role == UserRoles.USER
    assert user.is_superuser is False
