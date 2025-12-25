from sqlalchemy.ext.asyncio import AsyncSession

from core.logging import set_user_context
from core.security import verify_password
from crud.user import user_crud
from managers.exceptions import (
    InvalidCredentials,
    PermissionDenied,
    UserInactive,
)
from models import User
from models.user import UserRole


class AuthManager:
    """Менеджер авторизации."""

    def __init__(self, session: AsyncSession) -> None:
        """Инициализирует менеджер сессией базы данных."""
        self.session = session

    async def authenticate(self, login: str, password: str) -> User:
        """Аутентификация пользователя."""
        user = await user_crud.get_by_login(login=login, session=self.session)

        if not user or not verify_password(password, user.hashed_password):
            raise InvalidCredentials

        if not user.is_active:
            raise UserInactive

        return user

    async def authorize(
        self,
        user: User | None,
        *,
        allow_anonymous: bool,
        allowed_roles: tuple[UserRole, ...],
    ) -> User | None:
        """Авторизация пользователя."""
        if user is None:
            if allow_anonymous:
                return None
            raise InvalidCredentials()

        if not user.is_active:
            raise UserInactive()

        if not user.is_superuser:
            if user.role not in allowed_roles:
                raise PermissionDenied()

        set_user_context(
            user_id=user.id,
            username=user.username,
            email=user.email,
            role=user.role.name,
        )
        return user
