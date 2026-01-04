from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from core.exceptions import InvalidToken
from managers.exceptions import (
    BookingNotFound,
    BookingValidationError,
    CafeNotFound,
    InvalidCredentials,
    PermissionDenied,
    SlotNotFound,
    SlotValidationError,
    TableNotFound,
    UserAlreadyExists,
    UserInactive,
    UserNotFound,
)


def register_exception_handlers(app: FastAPI) -> None:  # noqa: C901
    """Регистрирует ошибки."""

    @app.exception_handler(PermissionDenied)
    async def permission_denied_handler(
        request: Request,
        exc: PermissionDenied,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": str(exc)},
        )

    @app.exception_handler(UserAlreadyExists)
    async def user_already_exists_handler(
        request: Request,
        exc: UserAlreadyExists,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(exc)},
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

    @app.exception_handler(BookingValidationError)
    async def booking_validation_handler(
        request: Request,
        exc: BookingValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={'detail': str(exc)},
        )

    @app.exception_handler(BookingNotFound)
    async def booking_not_found_handler(
        request: Request,
        exc: BookingNotFound,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={'detail': str(exc)},
        )

    @app.exception_handler(SlotValidationError)
    async def slot_validation_handler(
        request: Request,
        exc: SlotValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={'detail': str(exc)},
        )

    @app.exception_handler(SlotNotFound)
    async def slot_not_found_handler(
        request: Request,
        exc: SlotNotFound,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={'detail': str(exc)},
        )

    @app.exception_handler(CafeNotFound)
    async def cafe_not_found_handler(
        request: Request,
        exc: CafeNotFound,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={'detail': str(exc)},
        )

    @app.exception_handler(TableNotFound)
    async def table_not_found_handler(
        request: Request,
        exc: TableNotFound,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
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

    @app.exception_handler(UserNotFound)
    async def user_not_found_handler(
        request: Request,
        exc: UserNotFound,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={'detail': str(exc)},
        )
