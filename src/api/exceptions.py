from fastapi import HTTPException
from starlette import status


class UserAlreadyExistsHTTP(HTTPException):
    """Пользователь с такими данными уже существует."""

    def __init__(self, detail: str = 'Пользователь уже существует.') -> None:
        """Инициализирует HTTP-исключение."""
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class InvalidCredentialsHTTP(HTTPException):
    """Неверные или недействительные учетные данные."""

    def __init__(self) -> None:
        """Инициализирует HTTP-исключение."""
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Не удалось проверить учетные данные.',
            headers={'WWW-Authenticate': 'Bearer'},
        )


class UserInactiveHTTP(HTTPException):
    """Пользователь отключен и не может выполнять действия."""

    def __init__(self) -> None:
        """Инициализирует HTTP-исключение."""
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Пользователь неактивен',
        )


class UserNotFoundHTTP(HTTPException):
    """Пользователь не найден."""

    def __init__(self) -> None:
        """Инициализирует HTTP-исключение."""
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Пользователь не найден',
        )


class PermissionDeniedHTTP(HTTPException):
    """Недостаточно прав для выполнения операции."""

    def __init__(self, detail: str = 'Недостаточно прав') -> None:
        """Инициализирует HTTP-исключение."""
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )
