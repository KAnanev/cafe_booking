from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_async_session
from core.security import create_access_token
from managers.auth_manager import AuthManager
from schemas.auth import AuthRequest, AuthResponse

router = APIRouter()


@router.post(
    '/',
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
