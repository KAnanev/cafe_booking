from typing import Annotated, Optional

from pydantic import (
    ConfigDict,
    EmailStr,
    StringConstraints,
    model_validator,
)

from auth.domain.permissions.context import UserRole
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
    """Полная схема пользователя, как для чтения и базой валидации.

    Включает служебные поля: идентификатор (UUID), временные метки,
    статус активности и роль пользователя (enum: admin / manager / user).
    """

    role: UserRole


class UserCreate(UserBase):
    """Схема для приема данных при регистрации нового пользователя.

    Требует пароль и хотя бы один контакт (email или телефон).
    """

    model_config = ConfigDict(extra='forbid')

    password: PasswordStr

    @model_validator(mode='after')
    def validate_at_least_one_contact(self) -> 'UserCreate':
        """Проверяет, чтобы был указан хотя бы один контакт."""
        if self.email is None and self.phone is None:
            raise ValueError(
                'Необходимо указать хотя бы email или телефон.',
            )
        return self


class UserMeUpdate(BaseSchema):
    """Схема для частичного обновления своих данных пользователя."""

    username: Optional[UsernameStr] = None
    email: Optional[EmailStr] = None
    phone: Optional[PhoneStr] = None
    tg_id: Optional[TelegramStr] = None
    password: Optional[PasswordStr] = None

    model_config = ConfigDict(extra='forbid')


class UserAdminUpdate(UserMeUpdate):
    """Схема для частичного обновления пользователя администратором."""

    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserCreateDB(BaseSchema):
    """Служебная схема для записи пользователя в базу и CRUD.

    Используется только внутри сервисов и репозиториев. Не для API.
    """

    username: UsernameStr
    email: Optional[EmailStr]
    phone: Optional[PhoneStr]
    tg_id: Optional[str]
    hashed_password: HashedPasswordStr
    is_active: bool = True
    role: UserRole = UserRole.USER
    is_superuser: bool = False


class UserShortInfo(UUIDIDSchema, BaseSchema):
    """Краткая информация о пользователе."""

    username: UsernameStr
    email: Optional[EmailStr] = None
    phone: Optional[PhoneStr] = None
    tg_id: Optional[TelegramStr] = None
