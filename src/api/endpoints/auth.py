from fastapi import APIRouter, Depends, status

from api.dependencies.managers import get_auth_manager
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
    auth_manager: AuthManager = Depends(get_auth_manager),
) -> AuthResponse:
    """Возвращает токен для последующей авторизации пользователя."""
    user = await auth_manager.authenticate(
        login=data.login,
        password=data.password,
    )

    access_token = create_access_token(user.id)

    return AuthResponse(
        access_token=access_token,
        token_type='bearer',
    )
