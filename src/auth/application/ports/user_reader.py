from typing import Protocol

from auth.domain.models import AuthUser


class UserRepository(Protocol):
    """Интерфейс для работы с пользователями."""

    async def get_by_login(self, login: str) -> AuthUser | None:
        """Получает пользователя по логину."""
