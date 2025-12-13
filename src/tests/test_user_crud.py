# tests/test_user_crud.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from crud.user import user_crud
from models.user import UserRole
from schemas.user import UserCreate


@pytest.mark.asyncio
async def test_create_user_with_uuid(db_session: AsyncSession) -> None:
    """Тестирует создание пользователя через CRUD-функцию.

    Проверяет, что:
    - У созданного пользователя присутствует UUID-идентификатор (`id`);
    - Идентификатор не пустой (корректно сгенерирован);
    - Роль пользователя по умолчанию установлена как UserRole.USER.
    """
    user_data = UserCreate(
        username='ivan',
        login='ivan@example.ru',
        password='password',
    )
    user = await user_crud.create(session=db_session, obj_in=user_data)

    assert user.id is not None
    assert str(user.id) != ''
    assert user.role == UserRole.USER
