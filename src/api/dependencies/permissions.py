from http import HTTPStatus
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.users import get_current_user
from core.db import get_async_session
from crud.cafe import cafe_crud
from models.user import Roles, User


async def is_manager_or_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Разрешает доступ только менеджерам и админам."""

    if current_user.role in (Roles.MANAGER, Roles.ADMIN):
        return current_user
    raise HTTPException(
        status_code=HTTPStatus.FORBIDDEN,
        detail='Недостаточно прав.',
    )


async def can_manage_cafe(
    cafe_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> User:
    """Проверка права управления конкретным кафе."""

    if current_user.role == Roles.ADMIN:
        return current_user

    if current_user.role != Roles.MANAGER:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Недостаточно прав для управления этим кафе.',
        )

    managed_cafes = await cafe_crud.get_managed_cafes(
        session=session,
        user_id=current_user.id,
    )
    if any(cafe.id == cafe_id for cafe in managed_cafes):
        return current_user

    raise HTTPException(
        status_code=HTTPStatus.FORBIDDEN,
        detail='Пользователь не является менеджером этого кафе.',
    )
