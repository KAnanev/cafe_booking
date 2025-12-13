from collections.abc import Callable

import pytest
from sqlalchemy.exc import MultipleResultsFound
from sqlalchemy.ext.asyncio import AsyncSession

from crud.user import user_crud

from .fixtures.test_data import (
    TEST_EMAIL_1,
    TEST_EMAIL_2,
    TEST_EMAIL_3,
    TEST_EMAIL_4,
    TEST_EMAIL_5,
    TEST_EMAIL_6,
    TEST_EMAIL_7,
    TEST_PHONE_1,
    TEST_PHONE_2,
    TEST_PHONE_3,
    TEST_PHONE_4,
    TEST_PHONE_5,
    USERNAME_1,
    USERNAME_2,
    USERNAME_3,
    USERNAME_4,
    USERNAME_5,
    USERNAME_6,
    USERNAME_7,
    USERNAME_8,
    USERNAME_9,
)


@pytest.mark.asyncio
async def test_get_by_email_or_phone_found_by_email(
    db_session: AsyncSession,
    create_user: Callable,
    user_create_data: Callable,
) -> None:
    """Проверяет, что пользователь находится по совпадающему email.

    Даже если телефон не совпадает.
    """
    await create_user(
        email=TEST_EMAIL_1,
        phone=TEST_PHONE_1,
        username=USERNAME_1,
    )
    user_in = user_create_data(
        email=TEST_EMAIL_1,
        phone=TEST_PHONE_5,
        username=USERNAME_6,
    )

    found_user = await user_crud.get_by_email_or_phone(user_in, db_session)

    assert found_user is not None
    assert found_user.email == TEST_EMAIL_1
    assert found_user.phone == TEST_PHONE_1
    assert found_user.username == USERNAME_1


@pytest.mark.asyncio
async def test_get_by_email_or_phone_found_by_phone(
    db_session: AsyncSession,
    create_user: Callable,
    user_create_data: Callable,
) -> None:
    """Проверяет, что пользователь находится по совпадающему телефону.

    Даже если email не совпадает.
    """
    await create_user(
        email=TEST_EMAIL_2,
        phone=TEST_PHONE_1,
        username=USERNAME_2,
    )
    user_in = user_create_data(
        email=TEST_EMAIL_3,
        phone=TEST_PHONE_1,
        username=USERNAME_7,
    )

    found_user = await user_crud.get_by_email_or_phone(user_in, db_session)

    assert found_user is not None
    assert found_user.phone == TEST_PHONE_1
    assert found_user.username == USERNAME_2


@pytest.mark.asyncio
async def test_get_by_email_or_phone_not_found(
    db_session: AsyncSession,
    create_user: Callable,
    user_create_data: Callable,
) -> None:
    """Проверяет, что возвращается None, если ни email, ни телефон.

    Не совпадают ни с одним пользователем.
    """
    await create_user(
        email=TEST_EMAIL_4,
        phone=TEST_PHONE_4,
        username=USERNAME_3,
    )
    user_in = user_create_data(
        email=TEST_EMAIL_5,
        phone=TEST_PHONE_3,
        username=USERNAME_8,
    )

    found_user = await user_crud.get_by_email_or_phone(user_in, db_session)

    assert found_user is None


@pytest.mark.asyncio
async def test_get_by_email_or_phone_duplicate_found(
    db_session: AsyncSession,
    create_user: Callable,
    user_create_data: Callable,
) -> None:
    """Проверяет, что возникает MultipleResultsFound.

    Если один пользователь совпадает по email, а другой — по телефону.
    """
    await create_user(
        email=TEST_EMAIL_6,
        phone=TEST_PHONE_3,
        username=USERNAME_4,
    )
    await create_user(
        email=TEST_EMAIL_7,
        phone=TEST_PHONE_2,
        username=USERNAME_5,
    )

    user_in = user_create_data(
        email=TEST_EMAIL_6,
        phone=TEST_PHONE_2,
        username=USERNAME_9,
    )

    with pytest.raises(MultipleResultsFound):
        await user_crud.get_by_email_or_phone(user_in, db_session)
