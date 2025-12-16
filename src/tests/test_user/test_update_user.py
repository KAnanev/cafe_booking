from uuid import uuid4

import pytest
from fastapi import status
from httpx import AsyncClient

from models.user import User, UserRoles

from .fixtures.test_data import USERS_ROUTE


@pytest.mark.asyncio
async def test_admin_can_update_any_user(
    async_client: AsyncClient,
    admin_token: str,
    regular_user: User,
) -> None:
    """ADMIN может обновлять любого пользователя."""
    payload = {
        'username': 'updated_by_admin',
        'role': UserRoles.MANAGER,
        'is_active': False,
    }

    response = await async_client.patch(
        f'{USERS_ROUTE}{regular_user.id}',
        json=payload,
        headers={'Authorization': f'Bearer {admin_token}'},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data['username'] == 'updated_by_admin'
    assert data['role'] == UserRoles.MANAGER
    assert data['is_active'] is False


@pytest.mark.asyncio
async def test_manager_can_update_user_allowed_fields(
    async_client: AsyncClient,
    manager_token: str,
    regular_user: User,
) -> None:
    """MANAGER может обновлять пользователя (кроме role, is_active)."""
    payload = {
        'username': 'updated_by_manager',
        'email': 'manager_updated@example.ru',
    }

    response = await async_client.patch(
        f'{USERS_ROUTE}{regular_user.id}',
        json=payload,
        headers={'Authorization': f'Bearer {manager_token}'},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data['username'] == 'updated_by_manager'
    assert data['email'] == 'manager_updated@example.ru'


@pytest.mark.asyncio
async def test_manager_cannot_update_role(
    async_client: AsyncClient,
    manager_token: str,
    regular_user: User,
) -> None:
    """MANAGER не может менять role."""
    response = await async_client.patch(
        f'{USERS_ROUTE}{regular_user.id}',
        json={'role': UserRoles.ADMIN},
        headers={'Authorization': f'Bearer {manager_token}'},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_manager_cannot_update_is_active(
    async_client: AsyncClient,
    manager_token: str,
    regular_user: User,
) -> None:
    """MANAGER не может менять is_active."""
    response = await async_client.patch(
        f'{USERS_ROUTE}{regular_user.id}',
        json={'is_active': False},
        headers={'Authorization': f'Bearer {manager_token}'},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_user_cannot_update_self_via_id(
    async_client: AsyncClient,
    user_token: str,
    regular_user: User,
) -> None:
    """USER не может обновлять себя через /users/{id}."""
    response = await async_client.patch(
        f'{USERS_ROUTE}{regular_user.id}',
        json={'username': 'hack'},
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_user_cannot_update_other_user(
    async_client: AsyncClient,
    user_token: str,
    manager_user: User,
) -> None:
    """USER не может обновлять другого пользователя."""
    response = await async_client.patch(
        f'{USERS_ROUTE}{manager_user.id}',
        json={'username': 'hack'},
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_update_nonexistent_user(
    async_client: AsyncClient,
    admin_token: str,
) -> None:
    """Обновление несуществующего пользователя."""
    response = await async_client.patch(
        f'{USERS_ROUTE}{uuid4()}',
        json={'username': 'ghost'},
        headers={'Authorization': f'Bearer {admin_token}'},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
