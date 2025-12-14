from sqlalchemy.ext.asyncio import AsyncSession

from core.security import verify_password
from crud.user import user_crud
from managers.exceptions import InvalidCredentials, UserInactive
from models import User


class AuthManager:
    """Менеджер авторизации."""

    def __init__(self, session: AsyncSession) -> None:
        """Инициализирует менеджер сессией базы данных."""
        self.session = session

    async def authenticate(self, login: str, password: str) -> User:
        """Аутентификация пользователя."""
        user = await user_crud.get_by_login(login)

        if not user:
            raise InvalidCredentials

        if not verify_password(password, user.hashed_password):
            raise InvalidCredentials

        if not user.is_active:
            raise UserInactive

        return user
