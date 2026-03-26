from dataclasses import dataclass
from enum import StrEnum

from common.domain.base import BaseEntity


class UserRole(StrEnum):
    """Представляет роли пользователя в виде перечисления строк."""

    ADMIN = 'admin'
    MANAGER = 'manager'
    USER = 'user'


@dataclass
class User(BaseEntity):
    """Класс представляет пользователя в системе."""

    username: str
    hashed_password: str
    email: str | None = None
    phone: str | None = None
    tg_id: str | None = None
    role: UserRole = UserRole.USER
    is_superuser: bool = False

    def __post_init__(self) -> None:
        if not any([self.email, self.phone]):
            raise ValueError('Нужно указать почту или телефон.')

        if not self.username.strip():
            raise ValueError('Имя пользователя не может быть пустым.')

        if not self.hashed_password.strip():
            raise ValueError('Пароль не может быть пустым.')

        if self.is_superuser and self.role != UserRole.ADMIN:
            raise ValueError('Суперпользователь должен иметь роль admin.')
