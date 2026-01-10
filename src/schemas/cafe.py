from typing import Annotated, Optional
from uuid import UUID

from pydantic import ConfigDict, EmailStr, Field, StringConstraints

from core.constants import (
    CAFE_ADDRESS_MAX_LENGTH,
    CAFE_NAME_MAX_LENGTH,
    CAFE_NAME_MIN_LENGTH,
    DESCRIPTION_MAX_LENGTH,
    DESCRIPTION_MIN_LENGTH,
    PHONE_MAX_LENGTH,
)
from schemas.base import (
    ActiveSchema,
    BaseSchema,
    TimestampSchema,
    UUIDIDSchema,
)

CafeName = Annotated[
    str,
    StringConstraints(
        min_length=CAFE_NAME_MIN_LENGTH,
        max_length=CAFE_NAME_MAX_LENGTH,
    ),
]

CafeAddress = Annotated[
    str,
    StringConstraints(max_length=CAFE_ADDRESS_MAX_LENGTH),
]

CafePhone = Annotated[
    str,
    StringConstraints(max_length=PHONE_MAX_LENGTH),
]

CafeDescription = Annotated[
    str,
    StringConstraints(
        min_length=DESCRIPTION_MIN_LENGTH,
        max_length=DESCRIPTION_MAX_LENGTH,
    ),
]

ManagersIdRequired = Annotated[
    list[UUID],
    Field(min_length=1, description='Список id пользователей-менеджеров'),
]

ManagersIdOptional = Annotated[
    Optional[list[UUID]],
    Field(
        default=None,
        description='Полная замена списка менеджеров (если передано)',
    ),
]


class CafeManagerRead(UUIDIDSchema, BaseSchema):
    """Менеджер (вложение в CafeRead)."""

    model_config = ConfigDict(from_attributes=True)

    username: str
    email: EmailStr
    phone: Optional[
        Annotated[str, StringConstraints(max_length=PHONE_MAX_LENGTH)]
    ] = None
    tg_id: Optional[str] = None


class CafeBase(BaseSchema):
    """Базовые поля кафе."""

    name: CafeName
    address: CafeAddress
    phone: CafePhone
    description: CafeDescription
    photo_id: Optional[UUID] = None


class CafeCreate(CafeBase):
    """Создание кафе."""

    managers_id: ManagersIdRequired


class CafeUpdate(BaseSchema):
    """Частичное обновление кафе."""

    name: Optional[CafeName] = None
    address: Optional[CafeAddress] = None
    phone: Optional[CafePhone] = None
    description: Optional[CafeDescription] = None
    photo_id: Optional[UUID] = None

    managers_id: ManagersIdOptional
    is_active: Optional[bool] = None


class ManagersSchema(BaseSchema):
    """Поле с менеджером."""

    managers: list[CafeManagerRead] = Field(default_factory=list)


class CafeRead(
    TimestampSchema,
    ActiveSchema,
    ManagersSchema,
    CafeBase,
    UUIDIDSchema,
):
    """Ответ (list/get/create/patch)."""


class CafeReadShort(CafeBase, UUIDIDSchema):
    """Короткий ответ для booking."""
