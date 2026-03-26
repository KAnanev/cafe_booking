from dataclasses import dataclass
from enum import StrEnum


class UserRole(StrEnum):
    """Представляет роли пользователя в виде перечисления строк."""

    ADMIN = 'admin'
    MANAGER = 'manager'
    USER = 'user'


@dataclass
class User:
    """Класс представляет пользователя в системе."""

    username: str
    email: str | None
    phone: str | None
    tg_id: str | None
    hashed_password: str
    role: UserRole = UserRole.USER
    is_superuser: bool = False

    def __post_init__(self) -> None:
        if not any([self.email, self.phone]):
            raise ValueError('Нужно указать почту или телефон.')

        if not self.hashed_password:
            raise ValueError('Пароль не может быть пустым.')
