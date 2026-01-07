from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_async_session
from managers.auth_manager import AuthManager
from managers.cafe_manager import CafeManager
from managers.session_manager import SessionManager
from managers.slot_manager import SlotManager
from managers.table_manager import TableManager
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


def get_session_manager(
    session: AsyncSession = Depends(get_async_session),
) -> SessionManager:
    """Фабрика-зависимостей для SessionManager."""
    return SessionManager(session)


def get_cafe_manager(
    session: AsyncSession = Depends(get_async_session),
) -> CafeManager:
    """Фабрика-зависимостей для CafeManager."""
    return CafeManager(session)


def get_slot_manager(
    session: AsyncSession = Depends(get_async_session),
) -> SlotManager:
    """Фабрика-зависимостей для SlotManager."""
    return SlotManager(session)


def get_table_manager(
    session: AsyncSession = Depends(get_async_session),
) -> TableManager:
    """Фабрика-зависимостей для TableManager."""
    return TableManager(session)
