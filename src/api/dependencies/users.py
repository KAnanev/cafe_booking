from http import HTTPStatus
from typing import Awaitable, Callable
from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_async_session
from core.logging import set_user_context
from models.user import Roles, User

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    session: AsyncSession = Depends(get_async_session),
) -> User:
    """Текущий пользователь."""
    if credentials is None:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Необходимо авторизоваться.',
        )

    token = (credentials.credentials or '').strip()
    if not token:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Пустой токен авторизации.',
        )

    user: User | None = None
    try:
        user_id = UUID(token)
        result = await session.execute(
            select(User).where(User.id == user_id),
        )
        user = result.scalars().first()
    except ValueError:
        result = await session.execute(
            select(User).where(User.email == token),
        )
        user = result.scalars().first()

    if user is None:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Пользователь не найден.',
        )
    if hasattr(user, 'is_active') and not user.is_active:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Пользователь неактивен.',
        )

    # Устанавливаем контекст пользователя для логирования
    set_user_context(
        user_id=user.id,
        username=user.email,
        email=user.email,
        role=user.role.name if hasattr(user.role, 'name') else str(user.role),
    )
    return user


def required_role(role: Roles) -> Callable[[User], Awaitable[User]]:
    """Возвращает зависимость, проверяющую минимальную роль пользователя."""

    async def check_role(user: User = Depends(get_current_user)) -> User:
        if user.role < role:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail='Недостаточно прав.',
            )
        return user

    return check_role
