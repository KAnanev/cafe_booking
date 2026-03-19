from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


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

    def revoke(self) -> None:
        """Отзывает сессию."""
        self.is_active = False
