from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from crud.user import UserCRUD
from models import User


class UserProvider(Protocol):
    """Интерфейс для работы с пользователями."""

    async def get_by_login(self, login: str) -> User | None:
        """Получает пользователя по логину."""


class DBUserProvider:
    """Провайдер пользователей для работы с базой данных."""

    def __init__(self, crud: UserCRUD, session: AsyncSession) -> None:
        """Инициализация DBUserProvider."""
        self.crud = crud
        self.session = session

    async def get_by_login(self, login: str) -> User | None:
        """Получает пользователя по логину из базы данных."""
        return await self.crud.get_by_login(session=self.session, login=login)
