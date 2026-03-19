from typing import Protocol
from uuid import UUID

from auth.domain.entities import UserSession
from auth.domain.models import AuthUser


class PasswordService(Protocol):
    """Интерфейс для работы с паролями."""

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """Проверяет, соответствует ли хэш пароля хэшу введенного пароля."""
        ...

    def hash(self, plain_password: str) -> str:
        """Хэширует пароль для сохранения в базе данных."""
        ...


class TokenService(Protocol):
    """Токен-сервис для работы с JWT-токенами."""

    def create_access_token(self, user_id: UUID, user_session_id: UUID) -> str:
        """Создает JWT-токен для доступа."""


class UserRepository(Protocol):
    """Интерфейс для работы с пользователями."""

    async def get_by_login(self, login: str) -> AuthUser | None:
        """Получает пользователя по логину."""


class SessionRepository(Protocol):
    """Интерфейс для работы с сессиями."""

    async def get_by_id(self, user_session_id: UUID) -> UserSession | None:
        """Возвращает сессию по её идентификатору или None."""

    async def add(self, user_session: UserSession) -> UserSession:
        """Добавляет новую пользовательскую сессию."""
