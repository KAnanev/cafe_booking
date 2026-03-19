from sqlalchemy.ext.asyncio import AsyncSession

from auth.application.interfaces import UserRepository
from auth.domain.models import AuthUser
from crud.user import UserCRUD

from src.models import User


class SqlAlchemyUserRepository(UserRepository):
    """Класс для чтения данных аутентификации пользователя из базы данных."""

    def __init__(self, user_crud: UserCRUD, session: AsyncSession) -> None:
        """Конструктор класса."""
        self.user_crud = user_crud
        self.session = session

    async def get_by_login(self, login: str) -> AuthUser | None:
        """Асинхронный метод для получения данных аутентификации."""
        user: User | None = await self.user_crud.get_by_login(
            login=login,
            session=self.session,
        )
        if user is None:
            return None

        return AuthUser(
            id=user.id,
            hashed_password=user.hashed_password,
            is_active=user.is_active,
        )
