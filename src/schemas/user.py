from typing import Annotated, Optional

from pydantic import (
    ConfigDict,
    EmailStr,
    StringConstraints,
    model_validator,
)

from core.constants import (
    PASSWORD_HASH_MAX_LENGTH,
    PASSWORD_HASH_MIN_LENGTH,
    PASSWORD_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
    PHONE_PATTERN,
    TG_ID_MAX_LENGTH,
    TG_ID_MIN_LENGTH,
    USERNAME_MAX_LENGTH,
    USERNAME_MIN_LENGTH,
)
from models.user import UserRole
from schemas.base import (
    ActiveSchema,
    BaseSchema,
    TimestampSchema,
    UUIDIDSchema,
)

UsernameStr = Annotated[
    str,
    StringConstraints(
        min_length=USERNAME_MIN_LENGTH,
        max_length=USERNAME_MAX_LENGTH,
    ),
]

PasswordStr = Annotated[
    str,
    StringConstraints(
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH,
    ),
]

PhoneStr = Annotated[
    str,
    StringConstraints(pattern=PHONE_PATTERN),
]

TelegramStr = Annotated[
    str,
    StringConstraints(
        min_length=TG_ID_MIN_LENGTH,
        max_length=TG_ID_MAX_LENGTH,
    ),
]

HashedPasswordStr = Annotated[
    str,
    StringConstraints(
        min_length=PASSWORD_HASH_MIN_LENGTH,
        max_length=PASSWORD_HASH_MAX_LENGTH,
    ),
]


class UserBase(BaseSchema):
    """Базовая схема пользователя с основными контактными данными.

    Используется как родительский класс для создания, обновления и отображения.
    Телефон и email — опциональные, но хотя бы одно из них должно быть задано
    при регистрации (проверяется на уровне UserCreate).
    """

    username: UsernameStr
    email: Optional[EmailStr] = None
    phone: Optional[PhoneStr] = None
    tg_id: Optional[TelegramStr] = None


class UserDB(TimestampSchema, ActiveSchema, UserBase, UUIDIDSchema):
    """Полная схема пользователя, как она хранится в базе данных.

    Включает служебные поля: идентификатор (UUID), временные метки,
    флаг активности и роль пользователя (enum: admin / manager / user).
    """

    role: UserRole


class UserCreate(UserBase):
    """Схема входящих данных при регистрации нового пользователя.

    Требует пароль и хотя бы один контакт (email или телефон).
    """

    model_config = ConfigDict(extra='forbid')

    password: PasswordStr

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


class UserMeUpdate(BaseSchema):
    """Схема для обновления собственных данных пользователя."""

    username: Optional[UsernameStr] = None
    email: Optional[EmailStr] = None
    phone: Optional[PhoneStr] = None
    tg_id: Optional[TelegramStr] = None
    password: Optional[PasswordStr] = None

    model_config = ConfigDict(extra='forbid')


class UserAdminUpdate(UserMeUpdate):
    """Схема для обновления пользователя администратором."""

    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserCreateDB(BaseSchema):
    """Внутренняя схема создания пользователя для передачи в CRUD.

    Используется только в сервисном слое. Не применяется в API.
    """

    username: UsernameStr
    email: Optional[EmailStr]
    phone: Optional[PhoneStr]
    tg_id: Optional[str]
    hashed_password: HashedPasswordStr
    is_active: bool = True
    role: UserRole = UserRole.USER
    is_superuser: bool = False
