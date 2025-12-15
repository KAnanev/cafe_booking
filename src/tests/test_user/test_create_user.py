import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User, UserRoles
from schemas.user import UserCreate

from .fixtures.test_data import PAYLOAD, TEST_EMAIL_1, USERNAME_1, USERS_ROUTE


@pytest.mark.asyncio
async def test_create_user(
    async_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Создание пользователя с валидными данными.

    Проверяет:
    - успешный HTTP-ответ (201);
    - корректность возвращаемых данных;
    - сохранение пользователя в БД;
    - хеширование пароля.
    """
    response = await async_client.post(
        USERS_ROUTE,
        json=PAYLOAD,
    )

    assert response.status_code == 201

    data = response.json()

    assert data['username'] == USERNAME_1
    assert data['email'] == TEST_EMAIL_1
    assert data['role'] == UserRoles.USER
    assert data['is_active'] is True

    user: User | None = await db_session.get(User, data['id'])
    assert user is not None
    assert user.hashed_password != PAYLOAD['password']


@pytest.mark.asyncio
async def test_register_user_duplicate_email(
    async_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Попытка регистрации с уже существующим email.

    Проверяет, что повторная регистрация
    возвращает корректную бизнес-ошибку.
    """
    await async_client.post(USERS_ROUTE, json=PAYLOAD)

    response = await async_client.post(USERS_ROUTE, json=PAYLOAD)

    assert response.status_code == 400
    assert 'уже существует' in response.json()['detail']


@pytest.mark.asyncio
async def test_register_user_without_password(
    async_client: AsyncClient,
) -> None:
    """Регистрация без обязательного поля password.

    Проверяет, что запрос не проходит валидацию
    и возвращается ошибка 422.
    """
    payload: dict[str, str] = PAYLOAD.copy()
    payload.pop('password')

    response = await async_client.post(
        USERS_ROUTE,
        json=payload,
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_user_authorized_user_forbidden(
    async_client: AsyncClient,
    user_token: str,
    new_user_payload: UserCreate,
) -> None:
    """Авторизованный USER не может создавать пользователей."""
    response = await async_client.post(
        USERS_ROUTE,
        json=new_user_payload.model_dump(),
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == 403, response.text


@pytest.mark.asyncio
async def test_create_user_manager_allowed(
    async_client: AsyncClient,
    manager_token: str,
    new_user_payload: UserCreate,
) -> None:
    """MANAGER может создавать пользователей."""
    response = await async_client.post(
        USERS_ROUTE,
        json=new_user_payload.model_dump(),
        headers={'Authorization': f'Bearer {manager_token}'},
    )

    assert response.status_code == 201, response.text
    assert response.json()['username'] == new_user_payload.username


@pytest.mark.asyncio
async def test_create_user_admin_allowed(
    async_client: AsyncClient,
    admin_token: str,
    new_user_payload: UserCreate,
) -> None:
    """ADMIN может создавать пользователей."""
    response = await async_client.post(
        USERS_ROUTE,
        json=new_user_payload.model_dump(),
        headers={'Authorization': f'Bearer {admin_token}'},
    )

    assert response.status_code == 201, response.text
    assert response.json()['username'] == new_user_payload.username
