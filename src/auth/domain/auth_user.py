from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class AuthUser:
    """Класс для представления данных аутентификации пользователя."""

    id: UUID
    hashed_password: str
    is_active: bool
