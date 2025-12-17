import pytest
from httpx import AsyncClient

from models.user import User
from tests.test_user.fixtures.test_data import USERS_ROUTE


@pytest.mark.asyncio
async def test_get_users_admin_ok(
    async_client: AsyncClient,
    admin_token: str,
    admin_user: User,
    regular_user: User,
    manager_user: User,
) -> None:
    """ADMIN может получить список всех пользователей."""
    response = await async_client.get(
        USERS_ROUTE,
        headers={'Authorization': f'Bearer {admin_token}'},
    )

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3  # admin + user + manager

    usernames = {user['username'] for user in data}
    assert {
        admin_user.username,
        regular_user.username,
        manager_user.username,
    } <= usernames


@pytest.mark.asyncio
async def test_get_users_manager_ok(
    async_client: AsyncClient,
    manager_token: str,
) -> None:
    """MANAGER может получить список всех пользователей."""
    response = await async_client.get(
        USERS_ROUTE,
        headers={'Authorization': f'Bearer {manager_token}'},
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_users_user_forbidden(
    async_client: AsyncClient,
    user_token: str,
) -> None:
    """Обычному пользователю доступ запрещён."""
    response = await async_client.get(
        USERS_ROUTE,
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_users_unauthorized(
    async_client: AsyncClient,
) -> None:
    """Запрос без токена — 401 Unauthorized."""
    response = await async_client.get(USERS_ROUTE)

    assert response.status_code == 401
