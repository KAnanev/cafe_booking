from fastapi import APIRouter, Depends, status

from api.dependencies.managers import get_auth_manager, get_session_manager
from core.security import create_access_token
from managers.auth_manager import AuthManager
from managers.session_manager import SessionManager
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
    session_manager: SessionManager = Depends(get_session_manager),
) -> AuthResponse:
    """Возвращает токен для последующей авторизации пользователя."""
    user = await auth_manager.authenticate(
        login=data.login,
        password=data.password,
    )

    user_session = await session_manager.create(user_id=user.id)

    access_token = create_access_token(
        user_id=user.id,
        user_session_id=user_session.id,
    )

    return AuthResponse(
        access_token=access_token,
        token_type='bearer',
    )
