from typing import Any, Callable, Coroutine

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from api.exceptions import (
    InvalidCredentialsHTTP,
    PermissionDeniedHTTP,
    UserInactiveHTTP,
    UserNotFoundHTTP,
)
from core.db import get_async_session
from core.exceptions import InvalidToken
from core.security import decode_access_token
from crud.user import user_crud
from models.user import User, UserRoles
from core.logging import set_user_context

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl='/auth/login',
    auto_error=False,
)


async def get_current_user(
    session: AsyncSession = Depends(get_async_session),
    token: str = Depends(oauth2_scheme),
) -> User:
    """Получение текущего аутентифицированного пользователя.

    Извлекает JWT access-токен из заголовка Authorization,
    декодирует его, загружает пользователя из базы данных
    и проверяет его активность.
    """
    try:
        user_id = decode_access_token(token)
    except InvalidToken:
        raise InvalidCredentialsHTTP()

    user = await user_crud.get_by_id(obj_id=user_id, session=session)
    if not user:
        raise UserNotFoundHTTP()

    if not user.is_active:
        raise UserInactiveHTTP()
    # Устанавливаем контекст пользователя для логирования
    set_user_context(
        user_id=user.id,
        username=user.email,
        email=user.email,
        role=user.role.name if hasattr(user.role, 'name') else str(user.role),
    )
    return user


def require_role(
    *allowed_roles: UserRoles,
) -> Callable[..., Coroutine[Any, Any, User]]:
    """Проверка роли пользователя.

    Используется для ограничения доступа к эндпоинтам
    на основе роли (ADMIN, MANAGER, ...).
    """

    async def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        """Проверяет роль текущего пользователя."""
        if current_user.role not in allowed_roles:
            raise PermissionDeniedHTTP()
        return current_user

    return role_checker
