from fastapi import APIRouter, Depends, status

from api.dependencies.auth import get_login_use_case
from api.dependencies.managers import get_session_manager
from auth.use_cases.login import LoginUseCase
from core.security import create_access_token
from managers.session_manager import SessionManager
from schemas.auth import AuthRequest, AuthResponse

router = APIRouter()


@router.post(
    '/login',
    status_code=status.HTTP_200_OK,
    summary='Вход в систему',
)
async def login(
    data: AuthRequest,
    login_use_case: LoginUseCase = Depends(get_login_use_case),
    session_manager: SessionManager = Depends(get_session_manager),
) -> AuthResponse:
    """Обрабатывает запрос на вход в систему и возвращает токен доступа."""
    user = await login_use_case.execute(
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
