from typing import Protocol
from uuid import UUID

from accounts.auth.domain.user_session import UserSession as UserSessionEntity


class SessionRepository(Protocol):
    """Интерфейс для работы с сессиями."""

    async def get_by_id(
        self,
        user_session_id: UUID,
    ) -> UserSessionEntity | None:
        """Возвращает сессию по её идентификатору или None."""

    async def add(self, entity: UserSessionEntity) -> UserSessionEntity:
        """Добавляет новую пользовательскую сессию."""
