from typing import Callable

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from auth.domain.permissions.context import UserRole
from managers.exceptions import UserAlreadyExists
from managers.user_manager import UserManager


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
            hashed_password='plain_password',
        )

        manager = UserManager(session=db_session)
        result = await manager.create_user(user_in)

        assert result.username == user_in.username
        assert result.email == user_in.email
        assert result.phone == user_in.phone
        assert result.is_active is True
        assert result.role == UserRole.USER
        assert result.is_superuser is False

        from core.security import verify_password

        assert verify_password(
            'plain_password',
            result.hashed_password,
        )

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
