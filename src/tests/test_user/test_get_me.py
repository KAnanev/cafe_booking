import pytest
from httpx import AsyncClient

from models import User
from tests.test_user.fixtures.test_data import USERS_ROUTE


@pytest.mark.asyncio
async def test_get_me_ok(
    async_client: AsyncClient,
    user_token: str,
    regular_user: User,
) -> None:
    """Пользователь может получить себя."""
    response = await async_client.get(
        f'{USERS_ROUTE}me',
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == 200

    data = response.json()
    assert data['id'] == str(regular_user.id)
    assert data['username'] == regular_user.username
    assert data['email'] == regular_user.email


@pytest.mark.asyncio
async def test_get_me_unauthorized(
    async_client: AsyncClient,
) -> None:
    """Нет доступа неавторизованному пользователю."""
    response = await async_client.get(f'{USERS_ROUTE}me')

    assert response.status_code == 401
