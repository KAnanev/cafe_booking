from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_async_session
from core.security import create_access_token
from managers.auth_manager import AuthManager
from schemas.auth import AuthRequest, AuthResponse

router = APIRouter()


@router.post(
    '/login',
    status_code=status.HTTP_201_CREATED,
    summary='Вход в систему',
)
async def login(
    data: AuthRequest,
    session: AsyncSession = Depends(get_async_session),
) -> AuthResponse:
    """Возвращает токен для последующей авторизации пользователя."""
    manager = AuthManager(session)

    user = await manager.authenticate(
        login=data.login,
        password=data.password,
    )

    access_token = create_access_token(user.id)

    return AuthResponse(
        access_token=access_token,
        token_type='bearer',
    )


@router.post(
    '/token',
    include_in_schema=False,
    status_code=status.HTTP_200_OK,
    summary='Получение токена (Swagger OAuth2)',
)
async def swagger_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_async_session),
) -> AuthResponse:
    """Эндпоинт для Swagger OAuth2."""
    manager = AuthManager(session)

    user = await manager.authenticate(
        login=form_data.username,
        password=form_data.password,
    )

    access_token = create_access_token(user.id)

    return AuthResponse(
        access_token=access_token,
        token_type='bearer',
    )
