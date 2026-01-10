from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from core.constants import SESSION_TOUCH_THROTTLE_SECONDS, SESSION_TTL_SECONDS
from core.exceptions import InvalidToken
from crud.base import CRUDBase
from models.user_session import UserSession
from schemas.user_session import UserSessionCreate, UserSessionUpdate

session_crud = CRUDBase[UserSession, UserSessionCreate, UserSessionUpdate](
    UserSession,
)


class SessionManager:
    """Менеджер для работы с пользовательскими сессиями."""

    def __init__(self, session: AsyncSession) -> None:
        """Создаёт менеджер сессий с доступом к базе данных."""
        self.session = session

    async def get_by_id(self, user_session_id: UUID) -> UserSession | None:
        """Возвращает сессию по её идентификатору или None."""
        return await session_crud.get(
            obj_id=user_session_id,
            session=self.session,
        )

    async def create(self, user_id: UUID) -> UserSession:
        """Создаёт новую пользовательскую сессию."""
        last_activity = datetime.now(timezone.utc)
        expires_at = last_activity + timedelta(
            seconds=SESSION_TTL_SECONDS,
        )

        obj_in = UserSessionCreate(
            user_id=user_id,
            last_activity=last_activity,
            expires_at=expires_at,
        )
        return await session_crud.create(
            obj_in=obj_in,
            session=self.session,
        )

    def _validate(self, *, user_session: UserSession, now: datetime) -> None:
        """Проверяет, что сессия не истекла."""
        if user_session.expires_at <= now:
            raise InvalidToken()

    async def _touch(
        self,
        *,
        user_session: UserSession,
        now: datetime,
    ) -> UserSession:
        """Обновляет время активности и продлевает срок действия сессии."""
        if (
            user_session.last_activity is not None
            and (now - user_session.last_activity).total_seconds()
            < SESSION_TOUCH_THROTTLE_SECONDS
        ):
            return user_session

        data = UserSessionUpdate(
            last_activity=now,
            expires_at=now
            + timedelta(
                seconds=SESSION_TTL_SECONDS,
            ),
        )

        return await session_crud.update(
            db_obj=user_session,
            obj_in=data,
            session=self.session,
        )

    async def validate_touch(
        self,
        user_id: UUID,
        user_session_id: UUID,
    ) -> UserSession:
        """Проверяет валидность сессии и продлевает её срок действия."""
        user_session = await self.get_by_id(user_session_id)

        if user_session is None or user_session.user_id != user_id:
            raise InvalidToken()

        now = datetime.now(timezone.utc)

        self._validate(user_session=user_session, now=now)
        return await self._touch(user_session=user_session, now=now)
