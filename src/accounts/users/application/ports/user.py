from typing import Protocol

from users.domain.user import User


class UserRepository(Protocol):
    """Интерфейс для работы с пользователями."""

    async def create(self, user: User) -> User:
        """Создает пользователя."""
