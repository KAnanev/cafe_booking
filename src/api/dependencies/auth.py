from typing import Awaitable, Callable

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from api.dependencies.managers import (
    get_auth_manager,
    get_session_manager,
    get_user_manager,
)
from core.exceptions import InvalidToken
from core.security import decode_access_token
from managers.auth_manager import AuthManager
from managers.session_manager import SessionManager
from managers.user_manager import UserManager
from models import User
from models.user import UserRole

bearer_scheme = HTTPBearer(auto_error=False)


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    user_manager: UserManager = Depends(get_user_manager),
    session_manager: SessionManager = Depends(get_session_manager),
) -> User | None:
    """Возвращает текущего пользователя или None, Анонима."""
    if not credentials:
        return None

    try:
        user_id, user_session_id = decode_access_token(credentials.credentials)
        await session_manager.validate_touch(user_id, user_session_id)
        return await user_manager.get_by_id_or_none(user_id)

    except InvalidToken:
        return None


def require_role(
    *allowed_roles: UserRole,
    allow_anonymous: bool = False,
) -> Callable[..., Awaitable[User | None]]:
    """Dependency-фабрика для проверки роли пользователя."""

    async def role_checker(
        current_user: User | None = Depends(get_optional_user),
        manager: AuthManager = Depends(get_auth_manager),
    ) -> User | None:
        """Проверяет роль текущего пользователя."""
        return await manager.authorize(
            current_user,
            allow_anonymous=allow_anonymous,
            allowed_roles=allowed_roles,
        )

    return role_checker


require_auth = Depends(
    require_role(
        UserRole.ADMIN,
        UserRole.MANAGER,
        UserRole.USER,
    ),
)

require_admin = Depends(
    require_role(
        UserRole.ADMIN,
    ),
)

require_admin_or_manager = Depends(
    require_role(
        UserRole.ADMIN,
        UserRole.MANAGER,
    ),
)

require_anonymous_or_admin_or_manager = Depends(
    require_role(
        UserRole.ADMIN,
        UserRole.MANAGER,
        allow_anonymous=True,
    ),
)

optional_user = Depends(
    require_role(
        UserRole.ADMIN,
        UserRole.MANAGER,
        UserRole.USER,
        allow_anonymous=True,
    ),
)
