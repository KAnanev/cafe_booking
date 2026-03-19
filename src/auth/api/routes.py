from fastapi import APIRouter, Depends, status

from auth.api.dependencies import get_login_use_case
from auth.api.schemas import AuthRequest, AuthResponse
from auth.application.dto import LoginCommand
from auth.application.use_cases.login import LoginUseCase

router = APIRouter()


@router.post(
    '/login',
    status_code=status.HTTP_200_OK,
    summary='Вход в систему',
)
async def login(
    data: AuthRequest,
    login_use_case: LoginUseCase = Depends(get_login_use_case),
) -> AuthResponse:
    """Обрабатывает запрос на вход в систему и возвращает токен доступа."""
    result = await login_use_case.execute(
        LoginCommand(
            login=data.login,
            password=data.password,
        ),
    )

    return AuthResponse(
        access_token=result.access_token,
        token_type=result.token_type,
    )
