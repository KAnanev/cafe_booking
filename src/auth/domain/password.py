from typing import Protocol


class PasswordService(Protocol):
    """Интерфейс для работы с паролями."""

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """Проверяет, соответствует ли хэш пароля хэшу введенного пароля."""
        ...

    def hash(self, plain_password: str) -> str:
        """Хэширует пароль для сохранения в базе данных."""
        ...
