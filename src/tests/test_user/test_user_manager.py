from typing import Callable

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from managers.user_manager import UserManager

from .fixtures.test_data import (
    DEFAULT_PASSWORD,
    TEST_EMAIL_1,
    TEST_EMAIL_2,
    TEST_PHONE_1,
    TEST_PHONE_2,
    USERNAME_1,
    USERNAME_2,
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
            email=TEST_EMAIL_1,
            phone=TEST_PHONE_1,
            username=USERNAME_1,
            password=DEFAULT_PASSWORD,
        )
        manager = UserManager(session=db_session)

        result = await manager.create_user(user_in)

        assert result.email == TEST_EMAIL_1
        assert result.phone == TEST_PHONE_1
        assert result.username == USERNAME_1

        from core.security import verify_password
        from crud.user import user_crud

        db_user = await user_crud.get_by_email(
            user_in.email,
            session=db_session,
        )
        assert db_user is not None
        assert db_user.email == TEST_EMAIL_1
        assert verify_password(DEFAULT_PASSWORD, db_user.hashed_password)

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
        await create_user(
            email=TEST_EMAIL_1,
            phone=TEST_PHONE_2,
            username=USERNAME_1,
        )

        user_in = user_create_data(
            email=TEST_EMAIL_1,
            phone=TEST_PHONE_1,
            username=USERNAME_2,
        )
        manager = UserManager(session=db_session)

        with pytest.raises(
            ValueError,
            match='Пользователь test@example.com уже существует',
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
        await create_user(
            email=TEST_EMAIL_2,
            phone=TEST_PHONE_1,
            username=USERNAME_1,
        )

        user_in = user_create_data(
            email=TEST_EMAIL_1,
            phone=TEST_PHONE_1,
            username=USERNAME_2,
        )
        manager = UserManager(session=db_session)

        with pytest.raises(
            ValueError,
            match=r'Пользователь \+79991234567 уже существует',
        ):
            await manager.create_user(user_in)
