from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class UserSessionCreate(BaseModel):
    """Схема создания сессии."""

    user_id: UUID
    last_activity: datetime
    expires_at: datetime


class UserSessionUpdate(BaseModel):
    """Схема обновления сессии."""

    last_activity: datetime
    expires_at: datetime
