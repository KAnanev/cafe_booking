from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class UserSession:
    """Класс представляет пользовательскую сессию."""

    id: UUID
    user_id: UUID
    last_activity: datetime
    expires_at: datetime
    is_active: bool
