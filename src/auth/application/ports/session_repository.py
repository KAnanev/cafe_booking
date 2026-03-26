from typing import Protocol
from uuid import UUID

from auth.domain.user_session import UserSession


class SessionRepository(Protocol):
    """Интерфейс для работы с сессиями."""

    async def get_by_id(self, user_session_id: UUID) -> UserSession | None:
        """Возвращает сессию по её идентификатору или None."""

    async def add(self, user_session: UserSession) -> UserSession:
        """Добавляет новую пользовательскую сессию."""
