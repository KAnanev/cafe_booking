from typing import Protocol
from uuid import UUID


class TokenService(Protocol):
    """Токен-сервис для работы с JWT-токенами."""

    def create_access_token(self, user_id: UUID) -> str:
        """Создает JWT-токен для доступа."""
