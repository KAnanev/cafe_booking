from typing import Optional, Union
from uuid import UUID

from fastapi import Depends, Request
from fastapi_users import (
    BaseUserManager,
    FastAPIUsers,
    IntegerIDMixin,
    InvalidPasswordException,
)
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.constant import JWT_LIFETIME_SECONDS, MIN_PASSWORD_LENGTH
from src.core.db import get_async_session
from src.models.mixins import UUIDMixin
from src.models.user import User
from src.schemas.user import UserCreate
from fastapi.logger import logger


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)


bearer_transport = BearerTransport(tokenUrl='auth/jwt/login')


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.secret, lifetime_seconds=JWT_LIFETIME_SECONDS
    )


auth_backend = AuthenticationBackend(
    name='jwt',
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


class UserManager(UUIDMixin, BaseUserManager[User, UUID]):
    async def validate_password(
        self, password: str, user: Union[UserCreate, User]
    ) -> None:
        if len(password) < MIN_PASSWORD_LENGTH:
            raise InvalidPasswordException(
                reason=f'Пароль должен быть не менее '
                f'{MIN_PASSWORD_LENGTH} символов длиной'
            )
        if user.email in password:
            raise InvalidPasswordException(
                reason='Пароль не должен содержать электронную почту'
            )

    async def on_after_register(
        self, user: User, request: Optional[Request] = None
    ):
        logger.info(f'Пользователь {user.email} зарегистрирован.')


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


fastapi_users = FastAPIUsers[User, UUID](get_user_manager, [auth_backend])

current_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)
