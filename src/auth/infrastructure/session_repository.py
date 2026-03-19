from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.application.interfaces import SessionRepository
from auth.domain.entities import UserSession as UserSessionEntity
from models.user_session import UserSession as ORMUserSession


class SqlAlchemySessionRepository(SessionRepository):
    """Репозиторий для работы с пользовательскими сессиями через SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        """Создает новый экземпляр класса."""
        self.session = session

    async def add(self, entity: UserSessionEntity) -> UserSessionEntity:
        """Добавляет объект сущности в хранилище."""
        model = ORMUserSession(
            user_id=entity.user_id,
            last_activity=entity.last_activity,
            expires_at=entity.expires_at,
            is_active=entity.is_active,
        )
        self.session.add(model)
        await self.session.flush()

        return UserSessionEntity(
            id=model.id,
            user_id=model.user_id,
            last_activity=model.last_activity,
            expires_at=model.expires_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
            is_active=model.is_active,
        )

    async def get_by_id(
        self,
        user_session_id: UUID,
    ) -> UserSessionEntity | None:
        """Получает объект пользовательской сессии по его идентификатору."""
        stmt = select(ORMUserSession).where(
            ORMUserSession.id == user_session_id,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return UserSessionEntity(
            id=model.id,
            user_id=model.user_id,
            expires_at=model.expires_at,
            created_at=model.created_at,
        )
