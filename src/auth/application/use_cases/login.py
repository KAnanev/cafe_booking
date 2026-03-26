from datetime import datetime, timezone

from auth.application.dto import LoginCommand, LoginResult
from auth.application.exceptions import (
    AuthenticationFailed,
    InactiveAccount,
)
from auth.application.ports.uow import AuthUnitOfWork
from auth.application.security import (
    PasswordService,
    TokenService,
)
from auth.domain.entities import UserSession as UserSessionEntity


class LoginUseCase:
    """Класс для выполнения логина пользователя."""

    def __init__(
        self,
        uow: AuthUnitOfWork,
        password_service: PasswordService,
        token_service: TokenService,
    ) -> None:
        """Инициализация класса LoginUseCase."""
        self.uow = uow
        self.password_service = password_service
        self.token_service = token_service

    async def execute(self, command: LoginCommand) -> LoginResult:
        """Выполняет логин пользователя по логину и паролю."""
        async with self.uow:
            user = await self.uow.users.get_by_login(command.login)

            if not user:
                raise AuthenticationFailed()

            if not self.password_service.verify(
                command.password,
                user.hashed_password,
            ):
                raise AuthenticationFailed()

            if not user.is_active:
                raise InactiveAccount()

            now = datetime.now(timezone.utc)
            user_session = UserSessionEntity.start(user_id=user.id, now=now)
            saved_session = await self.uow.sessions.add(user_session)

            await self.uow.commit()

            access_token = self.token_service.create_access_token(
                user.id,
                saved_session.id,
            )

            return LoginResult(access_token=access_token)
