from auth.application.use_cases.exceptions import (
    InvalidCredentials,
    UserInactive,
)
from auth.domain.password import PasswordService
from auth.domain.permissions.context import UserContext
from auth.infrastructure.user_auth_reader import UserAuthReader


class LoginUseCase:
    """Класс для выполнения логина пользователя."""

    def __init__(
        self,
        user_reader: UserAuthReader,
        password_service: PasswordService,
    ) -> None:
        """Инициализация класса LoginUseCase."""
        self.user_reader = user_reader
        self.password_service = password_service

    async def execute(self, login: str, password: str) -> UserContext:
        """Выполняет логин пользователя по логину и паролю."""
        user = await self.user_reader.get_by_login(login)

        if not user:
            raise InvalidCredentials()

        if not self.password_service.verify(password, user.hashed_password):
            raise InvalidCredentials()

        if not user.is_active:
            raise UserInactive()

        return UserContext(
            id=user.id,
            role=user.role,
            is_active=user.is_active,
        )
