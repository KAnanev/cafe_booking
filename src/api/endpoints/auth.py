from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_async_session
from core.security import create_access_token
from managers.auth_manager import AuthManager
from managers.exceptions import InvalidCredentials, UserInactive
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

    try:
        user = await manager.authenticate(
            login=data.login,
            password=data.password,
        )
    except InvalidCredentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Неправильный логин или пароль',
        )
    except UserInactive:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Пользователь отключен',
        )

    access_token = create_access_token(user.id)

    return AuthResponse(
        access_token=access_token,
        token_type='bearer',
    )
