from auth.application.use_cases.login import LoginUseCase
from auth.infrastructure.db import AsyncSessionLocal
from auth.infrastructure.password_service import SecurePasswordService
from auth.infrastructure.token_service import SecureTokenService
from auth.infrastructure.uow.sqlalchemy_auth_uow import (
    SqlAlchemyAuthUnitOfWork,
)


def get_login_use_case() -> LoginUseCase:
    """Фабрика для получения экземпляра LoginUseCase."""
    uow = SqlAlchemyAuthUnitOfWork(AsyncSessionLocal)
    password_service = SecurePasswordService()
    token_service = SecureTokenService()

    return LoginUseCase(
        uow=uow,
        password_service=password_service,
        token_service=token_service,
    )
