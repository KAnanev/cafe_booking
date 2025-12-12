from typing import Any, AsyncGenerator, Optional, Union
from uuid import UUID

from fastapi import Depends, Request
from fastapi.logger import logger
from fastapi_users import (
    BaseUserManager,
    FastAPIUsers,
    InvalidPasswordException,
)
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.models import UserProtocol
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.constant import JWT_LIFETIME_SECONDS, MIN_PASSWORD_LENGTH
from core.db import get_async_session
from models.mixins import UUIDMixin
from models.user import User
from schemas.user import UserCreate


async def get_user_db(
    session: AsyncSession = Depends(get_async_session),
) -> AsyncGenerator[SQLAlchemyUserDatabase[UserProtocol | Any, Any], None]:
    """Получает экземпляр SQLAlchemyUserDatabase."""
    yield SQLAlchemyUserDatabase(session, User)


bearer_transport = BearerTransport(tokenUrl='auth/jwt/login')


def get_jwt_strategy() -> JWTStrategy:
    """Возвращает JWTStrategy с настроенными параметрами."""
    return JWTStrategy(
        secret=settings.secret,
        lifetime_seconds=JWT_LIFETIME_SECONDS,
    )


auth_backend = AuthenticationBackend(
    name='jwt',
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


class UserManager(UUIDMixin, BaseUserManager[User, UUID]):
    """Класс для управления пользователями."""

    async def validate_password(
        self,
        password: str,
        user: Union[UserCreate, User],
    ) -> None:
        """Проверяет пароль на соответствие требованиям."""
        if len(password) < MIN_PASSWORD_LENGTH:
            raise InvalidPasswordException(
                reason=f'Пароль должен быть не менее'
                f' {MIN_PASSWORD_LENGTH} символов длиной',
            )
        if user.email in password:
            raise InvalidPasswordException(
                reason='Пароль не должен содержать электронную почту',
            )

    async def on_after_register(
        self,
        user: User,
        request: Optional[Request] = None,
    ) -> None:
        """Логирует успешную регистрацию пользователя."""
        logger.info(f'Пользователь {user.email} зарегистрирован.')


async def get_user_manager(
    user_db: SQLAlchemyUserDatabase[User, UUID] = Depends(get_user_db),
) -> AsyncGenerator[UserManager, None]:
    """Получает экземпляр UserManager."""
    yield UserManager(user_db)


fastapi_users = FastAPIUsers[User, UUID](get_user_manager, [auth_backend])

current_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)
