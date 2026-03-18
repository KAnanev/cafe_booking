from auth.application.dto import LoginAuthData, LoginResponseData
from auth.application.ports import UserAuthReader
from auth.application.use_cases.exceptions import (
    AuthenticationFailed,
    InactiveAccount,
)
from auth.domain.password import PasswordService
from auth.domain.token import TokenService


class LoginUseCase:
    """Класс для выполнения логина пользователя."""

    def __init__(
        self,
        user_reader: UserAuthReader,
        password_service: PasswordService,
        token_service: TokenService,
    ) -> None:
        """Инициализация класса LoginUseCase."""
        self.user_reader = user_reader
        self.password_service = password_service
        self.token_service = token_service

    async def execute(self, data: LoginAuthData) -> LoginResponseData:
        """Выполняет логин пользователя по логину и паролю."""
        user = await self.user_reader.get_by_login(data.login)

        if not user:
            raise AuthenticationFailed()

        if not self.password_service.verify(
            data.password,
            user.hashed_password,
        ):
            raise AuthenticationFailed()

        if not user.is_active:
            raise InactiveAccount()

        token = self.token_service.create_access_token(user.id)

        return LoginResponseData(
            access_token=token,
            token_type='Bearer',
        )
