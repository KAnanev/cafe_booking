from datetime import datetime
from typing import Protocol
from uuid import UUID

from auth.application.dto import UserAuthData
from auth.domain.entities import UserSession


class UserAuthReader(Protocol):
    """Интерфейс для работы с пользователями."""

    async def get_by_login(self, login: str) -> UserAuthData | None:
        """Получает пользователя по логину."""


class UserSessionRepository(Protocol):
    """Интерфейс для работы с данными пользовательских сессий."""

    async def get_by_id(self, session_id: UUID) -> UserSession | None:
        """Асинхронный метод, для получения сущности UserSession."""

    async def create(
        self,
        user_id: UUID,
        last_activity: datetime,
        expires_at: datetime,
    ) -> UserSession:
        """Создает пользовательскую сессию."""
