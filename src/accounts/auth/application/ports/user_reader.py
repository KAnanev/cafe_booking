from typing import Protocol

from accounts.auth.domain.auth_user import AuthUser


class UserRepository(Protocol):
    """Интерфейс для работы с пользователями."""

    async def get_by_login(self, login: str) -> AuthUser | None:
        """Получает пользователя по логину."""
