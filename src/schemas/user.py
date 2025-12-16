import re
from typing import Optional

from pydantic import (
    ConfigDict,
    EmailStr,
    field_validator,
    model_validator,
)

from models.user import UserRole
from schemas.base import (
    ActiveSchema,
    BaseSchema,
    TimestampSchema,
    UUIDIDSchema,
)


class UserBase(BaseSchema):
    """Базовая схема пользователя с основными контактными данными.

    Используется как родительский класс для создания, обновления и отображения.
    Телефон и email — опциональные, но хотя бы одно из них должно быть задано
    при регистрации (проверяется на уровне UserCreate).
    """

    username: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    tg_id: Optional[str] = None
    role: Optional[UserRole] = None

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Проверяет, что номер телефона соответствует формату +79991234567.

        Args:
            v: Входное значение номера телефона (может быть None).

        Returns:
            Валидный номер телефона или None.

        Raises:
            ValueError: Если формат номера неверен.

        """
        if v is None:
            return None
        if not re.match(r'^\+7\d{10}$', v):
            raise ValueError(
                'Неверный формат телефона. Ожидается: +79991234567',
            )
        return v


class UserDB(TimestampSchema, ActiveSchema, UserBase, UUIDIDSchema):
    """Полная схема пользователя, как она хранится в базе данных.

    Включает служебные поля: идентификатор (UUID), временные метки,
    флаг активности и целочисленную роль (например, 0 — admin, 3 — user).
    """


class UserCreate(UserBase):
    """Схема входящих данных при регистрации нового пользователя.

    Требует пароль и хотя бы один контакт (email или телефон).
    """

    password: str

    @model_validator(mode='after')
    def validate_at_least_one_contact(self) -> 'UserCreate':
        """Обеспечивает, что указан хотя бы один: email или телефон.

        Returns:
            Экземпляр UserCreate, если валидация пройдена.

        Raises:
            ValueError: Если email и phone одновременно отсутствуют.

        """
        if self.email is None and self.phone is None:
            raise ValueError('Укажите электронную почту или номер телефона.')
        return self


class UserCreateDB(UserBase):
    """Схема входящих данных при передаче в CRUD."""

    hashed_password: str
    is_superuser: bool


class UserMeUpdate(BaseSchema):
    """Схема для обновления собственных данных пользователя."""

    username: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    tg_id: Optional[str] = None
    password: Optional[str] = None

    model_config = ConfigDict(extra='forbid')


class UserAdminUpdate(UserMeUpdate):
    """Схема для обновления пользователя администратором."""

    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
