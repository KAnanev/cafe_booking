from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from auth.domain.permissions.context import UserRole
from models import User


@dataclass(frozen=True)
class UserAuthData:
    """Класс для представления данных аутентификации пользователя."""

    id: UUID
    login: str
    hashed_password: str
    role: UserRole
    is_active: bool


class UserAuthReader(Protocol):
    """Интерфейс для работы с пользователями."""

    async def get_by_login(self, login: str) -> User | None:
        """Получает пользователя по логину."""
