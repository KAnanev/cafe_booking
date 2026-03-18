from dataclasses import dataclass
from uuid import UUID

from auth.domain.permissions.context import UserRole


@dataclass(frozen=True)
class UserAuthData:
    """Класс для представления данных аутентификации пользователя."""

    id: UUID
    login: str
    hashed_password: str
    role: UserRole
    is_active: bool


@dataclass(frozen=True)
class LoginAuthData:
    """Класс для хранения данных аутентификации."""

    login: str
    password: str


@dataclass(frozen=True)
class LoginResponseData:
    """Класс для хранения данных ответа при успешной авторизации."""

    access_token: str
    token_type: str
