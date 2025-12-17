import pytest
from httpx import AsyncClient

from models.user import User
from tests.test_user.fixtures.test_data import USERS_ROUTE


@pytest.mark.asyncio
async def test_user_can_update_self(
    async_client: AsyncClient,
    user_token: str,
    regular_user: User,
) -> None:
    """Пользователь может менять себя."""
    payload = {
        'username': 'new_username',
    }

    response = await async_client.patch(
        f'{USERS_ROUTE}me',
        json=payload,
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == 200

    data = response.json()
    assert data['id'] == str(regular_user.id)
    assert data['username'] == 'new_username'


@pytest.mark.asyncio
async def test_user_cannot_update_role_via_me(
    async_client: AsyncClient,
    user_token: str,
) -> None:
    """Пользователь не может обновлять запрещённые поля."""
    response = await async_client.patch(
        f'{USERS_ROUTE}me',
        json={'role': 'ADMIN'},
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == 422 or response.status_code == 403
