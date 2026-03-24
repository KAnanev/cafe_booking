from typing import Protocol
from uuid import UUID


class PasswordService(Protocol):
    """Сервис для работы с паролями.

    Предоставляет методы для хэширования пароля и проверки его соответствия
    сохраненному хэшу.
    """

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """Проверяет, соответствует ли хэш пароля хэшу введенного пароля."""
        ...

    def hash(self, plain_password: str) -> str:
        """Хэширует пароль для сохранения в базе данных."""
        ...


class TokenService(Protocol):
    """Протокол для работы с токенами.

    Определяет интерфейс для создания JWT-токенов доступа.
    """

    def create_access_token(self, user_id: UUID, user_session_id: UUID) -> str:
        """Создает JWT-токен для доступа."""
