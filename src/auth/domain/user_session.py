from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID

SESSION_TTL_SECONDS = 3600 * 24 * 7


@dataclass
class UserSession:
    """Класс представляет сессию пользователя."""

    user_id: UUID
    last_activity: datetime
    expires_at: datetime

    id: UUID | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    is_active: bool = True

    @classmethod
    def start(
        cls,
        user_id: UUID,
        now: datetime,
    ) -> 'UserSession':
        """Создает новый экземпляр сессии пользователя."""
        return cls(
            user_id=user_id,
            last_activity=now,
            expires_at=cls.calculate_expires_at(now),
        )

    @staticmethod
    def calculate_expires_at(last_activity: datetime) -> datetime:
        """Метод для вычисления истечения срока действия токена."""
        return last_activity + timedelta(seconds=SESSION_TTL_SECONDS)

    def revoke(self) -> None:
        """Отзывает сессию."""
        self.is_active = False
