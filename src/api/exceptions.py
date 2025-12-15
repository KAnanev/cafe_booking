from fastapi import HTTPException
from starlette import status


class InvalidCredentialsHTTP(HTTPException):
    """Кастомное исключение InvalidCredential.

    Когда пользователь с указанным логином не найден.
    """

    def __init__(self) -> None:
        """Инициализатор класса."""
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Не удалось проверить учетные данные.',
            headers={'WWW-Authenticate': 'Bearer'},
        )


class UserInactiveHTTP(HTTPException):
    """Кастомное исключение InvalidCredential.

    Когда пользователь отключен.
    """

    def __init__(self) -> None:
        """Инициализатор класса."""
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Пользователь неактивен',
        )


class UserNotFoundHTTP(HTTPException):
    """Кастомное исключение UserNotFound.

    Когда пользователь не найден.
    """

    def __init__(self) -> None:
        """Инициализатор класса."""
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Пользователь не найден',
        )


class PermissionDeniedHTTP(HTTPException):
    """403 Forbidden — недостаточно прав для выполнения операции."""

    def __init__(self, detail: str = 'Недостаточно прав') -> None:
        """Инициализатор класса."""
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )
