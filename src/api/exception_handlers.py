from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from core.exceptions import InvalidToken
from managers.exceptions import (
    InvalidCredentials,
    PermissionDenied,
    UserAlreadyExists,
    UserInactive,
)


def register_exception_handlers(app: FastAPI) -> None:
    """Регистрирует ошибки."""

    @app.exception_handler(PermissionDenied)
    async def permission_denied_handler(
        request: Request,
        exc: PermissionDenied,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={'detail': str(exc)},
        )

    @app.exception_handler(UserAlreadyExists)
    async def user_already_exists_handler(
        request: Request,
        exc: UserAlreadyExists,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,  # лучше 409
            content={'detail': str(exc)},
        )

    @app.exception_handler(InvalidCredentials)
    async def invalid_credentials_handler(
        request: Request,
        exc: InvalidCredentials,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={'detail': str(exc)},
            headers={'WWW-Authenticate': 'Bearer'},
        )

    @app.exception_handler(UserInactive)
    async def user_inactive_handler(
        request: Request,
        exc: UserInactive,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={'detail': str(exc)},
        )

    @app.exception_handler(InvalidToken)
    async def invalid_token_handler(
        request: Request,
        exc: InvalidToken,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={'detail': str(exc)},
        )
