from fastapi import HTTPException
from starlette import status


class UserNotFoundHTTP(HTTPException):
    """Пользователь не найден."""

    def __init__(self) -> None:
        """Инициализирует HTTP-исключение."""
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Пользователь не найден',
        )
