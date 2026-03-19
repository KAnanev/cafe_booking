from auth.application.dto import LoginCommand, LoginResult
from auth.application.exceptions import (
    AuthenticationFailed,
    InactiveAccount,
)
from auth.application.interfaces import (
    PasswordService,
    TokenService,
    UserRepository,
)


class LoginUseCase:
    """Класс для выполнения логина пользователя."""

    def __init__(
        self,
        user_repo: UserRepository,
        password_service: PasswordService,
        token_service: TokenService,
    ) -> None:
        """Инициализация класса LoginUseCase."""
        self.user_repo = user_repo
        self.password_service = password_service
        self.token_service = token_service

    async def execute(self, command: LoginCommand) -> LoginResult:
        """Выполняет логин пользователя по логину и паролю."""
        user = await self.user_repo.get_by_login(command.login)

        if not user:
            raise AuthenticationFailed()

        if not self.password_service.verify(
            command.password,
            user.hashed_password,
        ):
            raise AuthenticationFailed()

        if not user.is_active:
            raise InactiveAccount()

        access_token = self.token_service.create_access_token(user.id)

        return LoginResult(access_token=access_token)
