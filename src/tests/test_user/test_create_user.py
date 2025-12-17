import pytest
from httpx import AsyncClient

from models.user import UserRole
from schemas.user import UserCreate

from .fixtures.test_data import USERS_ROUTE


@pytest.mark.asyncio
async def test_create_user(
    async_client: AsyncClient,
    new_user_payload: UserCreate,
) -> None:
    """Создание пользователя с валидными данными."""
    response = await async_client.post(
        USERS_ROUTE,
        json=new_user_payload.model_dump(),
    )

    assert response.status_code == 201

    data = response.json()

    assert data['username'] == new_user_payload.username
    assert data['email'] == new_user_payload.email
    assert data['role'] == UserRole.USER
    assert data['is_active'] is True


@pytest.mark.asyncio
async def test_register_user_duplicate_email(
    async_client: AsyncClient,
    new_user_payload: UserCreate,
) -> None:
    """Тест на дубликат email."""
    await async_client.post(
        USERS_ROUTE,
        json=new_user_payload.model_dump(),
    )

    response = await async_client.post(
        USERS_ROUTE,
        json=new_user_payload.model_dump(),
    )

    assert response.status_code == 409
    assert 'уже существует' in response.json()['detail']


@pytest.mark.asyncio
async def test_register_user_without_password(
    async_client: AsyncClient,
    new_user_payload: UserCreate,
) -> None:
    """Тест на отсутствие пароля."""
    payload = new_user_payload.model_dump()
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

    assert response.status_code == 403


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

    assert response.status_code == 201
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

    assert response.status_code == 201
    assert response.json()['username'] == new_user_payload.username
