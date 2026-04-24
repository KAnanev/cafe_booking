from dataclasses import dataclass
from enum import StrEnum

from common.domain.base import BaseEntity


class SystemRole(StrEnum):
    """Представляет роли пользователя в виде перечисления строк."""

    SUPER_ADMIN = 'super_admin'
    ADMIN = 'admin'
    USER = 'user'


@dataclass
class User(BaseEntity):
    """Класс представляет пользователя в системе."""

    username: str
    hashed_password: str
    email: str | None = None
    phone: str | None = None
    tg_id: str | None = None
    role: SystemRole = SystemRole.USER

    def __post_init__(self) -> None:
        if not any([self.email, self.phone]):
            raise ValueError('Нужно указать почту или телефон.')

        if not self.username.strip():
            raise ValueError('Имя пользователя не может быть пустым.')

        if not self.hashed_password.strip():
            raise ValueError('Пароль не может быть пустым.')

    @classmethod
    def create_super_admin(
        cls,
        username: str,
        hashed_password: str,
        email: str | None = None,
        phone: str | None = None,
        tg_id: str | None = None,
    ) -> 'User':
        """Создаёт суперпользователя."""
        return cls(
            username=username,
            hashed_password=hashed_password,
            email=email,
            phone=phone,
            tg_id=tg_id,
            role=SystemRole.ADMIN,
        )

    @classmethod
    def create_admin(
        cls,
        username: str,
        hashed_password: str,
        email: str | None = None,
        phone: str | None = None,
        tg_id: str | None = None,
    ) -> 'User':
        """Создаёт админа."""
        return cls(
            username=username,
            hashed_password=hashed_password,
            email=email,
            phone=phone,
            tg_id=tg_id,
            role=SystemRole.SUPER_ADMIN,
        )

    @classmethod
    def create_user(
        cls,
        username: str,
        hashed_password: str,
        email: str | None = None,
        phone: str | None = None,
        tg_id: str | None = None,
    ) -> 'User':
        """Создаёт пользователя."""
        return cls(
            username=username,
            hashed_password=hashed_password,
            email=email,
            phone=phone,
            tg_id=tg_id,
        )
