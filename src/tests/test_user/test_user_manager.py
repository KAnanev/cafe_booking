from typing import Callable

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from managers.exceptions import UserAlreadyExists
from managers.user_manager import UserManager

from .fixtures.test_data import (
    DEFAULT_HASH,
)


class TestUserManager:
    """Тесты для UserManager."""

    @pytest.mark.asyncio
    async def test_create_user_success(
        self,
        db_session: AsyncSession,
        user_create_data: Callable,
    ) -> None:
        """Тестирует успешное создание пользователя."""
        user_in = user_create_data(
            username='user',
        )
        manager = UserManager(session=db_session)

        result = await manager.create_user(user_in)

        assert result.email == user_in.email
        assert result.phone == user_in.phone
        assert result.username == user_in.username

        from core.security import verify_password
        from crud.user import user_crud

        db_user = await user_crud.get_by_email(
            user_in.email,
            session=db_session,
        )
        assert db_user is not None
        assert db_user.email == user_in.email
        assert verify_password(DEFAULT_HASH, db_user.hashed_password)

    @pytest.mark.asyncio
    async def test_create_user_email_already_exists(
        self,
        db_session: AsyncSession,
        create_user: Callable,
        user_create_data: Callable,
    ) -> None:
        """Тест ошибки при попытке создания пользователя.

        C уже существующим email.
        """
        user = await create_user(
            username='user',
        )

        user_in = user_create_data(
            username='user',
            email=user.email,
        )
        manager = UserManager(session=db_session)

        with pytest.raises(
            UserAlreadyExists,
        ):
            await manager.create_user(user_in)

    @pytest.mark.asyncio
    async def test_create_user_phone_already_exists(
        self,
        db_session: AsyncSession,
        create_user: Callable,
        user_create_data: Callable,
    ) -> None:
        """Тестирует ошибку при попытке создания пользователя.

        С уже существующим телефоном.
        """
        user = await create_user(
            username='user',
        )

        user_in = user_create_data(
            username='user',
            phone=user.phone,
        )
        manager = UserManager(session=db_session)

        with pytest.raises(
            UserAlreadyExists,
        ):
            await manager.create_user(user_in)
