from fastapi import HTTPException, status


class InvalidCredentials(HTTPException):
    """Кастомное исключение InvalidCredential.

    Когда пользователь с указанным логином не найден.
    """

    def __init__(self) -> None:
        """Инициализатор класса."""
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid authentication credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )


class UserInactive(HTTPException):
    """Кастомное исключение InvalidCredential.

    Когда пользователь отключен.
    """

    def __init__(self) -> None:
        """Инициализатор класса."""
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='User is inactive',
        )
