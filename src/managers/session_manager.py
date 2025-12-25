from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.constants import JWT_LIFETIME_SECONDS
from crud.base import CRUDBase
from models.user_session import UserSession


class UserSessionCreate(BaseModel):
    """Схема создания сессии."""

    user_id: UUID
    last_activity: datetime
    expires_at: datetime


session_crud = CRUDBase[UserSession, UserSessionCreate, Any](UserSession)


class SessionManager:
    """Менеджер сессий."""

    def __init__(self, session: AsyncSession) -> None:
        """Инициализирует менеджер сессией базы данных."""
        self.session = session

    async def create(self, user_id: UUID) -> UserSession:
        """Создать сессию."""
        last_activity = datetime.now(timezone.utc)
        expires_at = last_activity + timedelta(seconds=JWT_LIFETIME_SECONDS)

        obj_in = UserSessionCreate(
            user_id=user_id,
            last_activity=last_activity,
            expires_at=expires_at,
        )
        return await session_crud.create(obj_in=obj_in, session=self.session)
