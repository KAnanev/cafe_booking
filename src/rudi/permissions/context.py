import uuid
from dataclasses import dataclass
from enum import StrEnum

from core.constants import ROLE_ADMIN, ROLE_MANAGER, ROLE_USER


class UserRole(StrEnum):
    """Роли пользователя."""

    USER = ROLE_USER
    MANAGER = ROLE_MANAGER
    ADMIN = ROLE_ADMIN


@dataclass(frozen=True)
class UserContext:
    """Контекст пользователя для проверки разрешений."""

    id: uuid.UUID
    role: UserRole
    is_active: bool
