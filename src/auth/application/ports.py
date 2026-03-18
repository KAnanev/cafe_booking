from typing import Protocol

from auth.application.dto import UserAuthData


class UserAuthReader(Protocol):
    """Интерфейс для работы с пользователями."""

    async def get_by_login(self, login: str) -> UserAuthData | None:
        """Получает пользователя по логину."""
