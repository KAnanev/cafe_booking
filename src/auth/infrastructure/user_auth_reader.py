from sqlalchemy.ext.asyncio import AsyncSession

from auth.application.dto import UserAuthData
from auth.application.ports import UserAuthReader
from auth.domain.permissions.context import UserRole
from crud.user import UserCRUD

from src.models import User


class DBUserAuthReader(UserAuthReader):
    """Класс для чтения данных аутентификации пользователя из базы данных."""

    def __init__(self, user_crud: UserCRUD, session: AsyncSession) -> None:
        """Конструктор класса."""
        self.user_crud = user_crud
        self.session = session

    async def get_by_login(self, login: str) -> UserAuthData | None:
        """Асинхронный метод для получения данных аутентификации."""
        user: User | None = await self.user_crud.get_by_login(
            login=login,
            session=self.session,
        )
        if user is None:
            return None

        return UserAuthData(
            id=user.id,
            login=user.username if user.username else user.email,
            hashed_password=user.hashed_password,
            role=UserRole(user.role),
            is_active=user.is_active,
        )
