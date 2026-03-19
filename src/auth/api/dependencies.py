from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.application.use_cases.login import LoginUseCase
from auth.infrastructure.password_service import SecurePasswordService
from auth.infrastructure.session_repository import SqlAlchemySessionRepository
from auth.infrastructure.token_service import SecureTokenService
from auth.infrastructure.user_repository import SqlAlchemyUserRepository
from core.db import get_async_session
from crud.user import user_crud


def get_login_use_case(
    session: AsyncSession = Depends(get_async_session),
) -> LoginUseCase:
    """Фабрика для получения экземпляра LoginUseCase."""
    user_repo = SqlAlchemyUserRepository(user_crud, session)
    session_repo = SqlAlchemySessionRepository(session)
    password_service = SecurePasswordService()
    token_service = SecureTokenService()

    return LoginUseCase(
        user_repo=user_repo,
        password_service=password_service,
        token_service=token_service,
        session_repo=session_repo,
    )
