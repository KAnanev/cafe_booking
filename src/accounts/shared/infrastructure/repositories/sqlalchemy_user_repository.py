from shared.application.ports.user_repository import UserRepository
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from accounts.auth.domain.auth_user import AuthUser
from models.user import User as ORMUser


class SqlAlchemyUserRepository(UserRepository):
    """Класс для чтения данных аутентификации пользователя из базы данных."""

    def __init__(self, session: AsyncSession) -> None:
        """Конструктор класса."""
        self.session = session

    async def get_by_login(self, login: str) -> AuthUser | None:
        """Асинхронный метод для получения данных аутентификации."""
        stmt = select(ORMUser).where(
            or_(ORMUser.email == login, ORMUser.phone == login),
        )

        result = await self.session.execute(stmt)
        user: ORMUser | None = result.scalar_one_or_none()

        if user is None:
            return None

        return AuthUser(
            id=user.id,
            hashed_password=user.hashed_password,
            is_active=user.is_active,
        )
