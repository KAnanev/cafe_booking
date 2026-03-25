from datetime import datetime, timedelta, timezone

from auth.application.dto import LoginCommand, LoginResult
from auth.application.exceptions import (
    AuthenticationFailed,
    InactiveAccount,
)
from auth.application.interfaces import (
    PasswordService,
    TokenService,
)
from auth.application.ports.uow import AuthUnitOfWork
from auth.domain.entities import UserSession as UserSessionEntity

SESSION_TTL_SECONDS = 3600 * 24 * 7


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

            last_activity = datetime.now(timezone.utc)
            expires_at = last_activity + timedelta(
                seconds=SESSION_TTL_SECONDS,
            )

            session = await self.uow.sessions.add(
                UserSessionEntity(
                    user_id=user.id,
                    last_activity=last_activity,
                    expires_at=expires_at,
                ),
            )

            await self.uow.commit()

            access_token = self.token_service.create_access_token(
                user.id,
                session.id,
            )

            return LoginResult(access_token=access_token)
