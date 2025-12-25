from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_async_session
from managers.auth_manager import AuthManager
from managers.user_manager import UserManager


def get_auth_manager(
    session: AsyncSession = Depends(get_async_session),
) -> AuthManager:
    """Фабрика-зависимостей для AuthManager."""
    return AuthManager(session)


def get_user_manager(
    session: AsyncSession = Depends(get_async_session),
) -> UserManager:
    """Фабрика-зависимостей для UserManager."""
    return UserManager(session)
