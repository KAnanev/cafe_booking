from auth.domain.password import PasswordService
from auth.providers.user_provider import UserProvider
from auth.use_cases.exceptions import InvalidCredentials, UserInactive
from models import User


class LoginUseCase:
    """Класс для выполнения логина пользователя."""

    def __init__(
        self,
        user_provider: UserProvider,
        password_service: PasswordService,
    ) -> None:
        """Инициализация класса LoginUseCase."""
        self.user_provider = user_provider
        self.password_service = password_service

    async def execute(self, login: str, password: str) -> User:
        """Выполняет логин пользователя по логину и паролю."""
        user = await self.user_provider.get_by_login(login=login)

        if not user:
            raise InvalidCredentials()

        if not self.password_service.verify(password, user.hashed_password):
            raise InvalidCredentials()

        if not user.is_active:
            raise UserInactive()

        return user
