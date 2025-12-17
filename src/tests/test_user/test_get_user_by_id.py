from http import HTTPStatus
from uuid import uuid4

import pytest
from httpx import AsyncClient

from models import User
from tests.test_user.fixtures.test_data import USERS_ROUTE


@pytest.mark.asyncio
async def test_get_user_by_id_admin(
    async_client: AsyncClient,
    admin_token: str,
    regular_user: User,
) -> None:
    """Тест: ADMIN получает пользователя по ID."""
    response = await async_client.get(
        f'{USERS_ROUTE}{regular_user.id}',
        headers={'Authorization': f'Bearer {admin_token}'},
    )

    assert response.status_code == HTTPStatus.OK

    data = response.json()
    assert data['id'] == str(regular_user.id)
    assert data['username'] == regular_user.username


@pytest.mark.asyncio
async def test_get_user_by_id_manager(
    async_client: AsyncClient,
    manager_token: str,
    regular_user: User,
) -> None:
    """Тест: MANAGER тоже имеет доступ."""
    response = await async_client.get(
        f'{USERS_ROUTE}{regular_user.id}',
        headers={'Authorization': f'Bearer {manager_token}'},
    )

    assert response.status_code == HTTPStatus.OK


@pytest.mark.asyncio
async def test_get_user_by_id_user_forbidden(
    async_client: AsyncClient,
    user_token: str,
    regular_user: User,
) -> None:
    """Тест: USER — доступ запрещён."""
    response = await async_client.get(
        f'{USERS_ROUTE}{regular_user.id}',
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_get_user_by_id_unauthorized(
    async_client: AsyncClient,
    regular_user: User,
) -> None:
    """Тест: без токена (аноним)."""
    response = await async_client.get(
        f'{USERS_ROUTE}{regular_user.id}',
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(
    async_client: AsyncClient,
    admin_token: str,
) -> None:
    """Тест: пользователь не найден."""
    response = await async_client.get(
        f'{USERS_ROUTE}{uuid4()}',
        headers={'Authorization': f'Bearer {admin_token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
