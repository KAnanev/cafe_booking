from pydantic import ConfigDict, Field

from core.constants import (
    CAFE_ADDRESS_MAX_LENGTH,
    CAFE_NAME_MAX_LENGTH,
    CAFE_NAME_MIN_LENGTH,
    DESCRIPTION_MAX_LENGTH,
    DESCRIPTION_MIN_LENGTH,
    PHONE_MAX_LENGTH,
    UUID_LENGTH,
)
from schemas.base import (
    ActiveSchema,
    BaseSchema,
    TimestampSchema,
    UUIDIDSchema,
)


class CafeBase(BaseSchema):
    """Базовые поля кафе."""

    name: str = Field(
        ...,
        min_length=CAFE_NAME_MIN_LENGTH,
        max_length=CAFE_NAME_MAX_LENGTH,
    )
    address: str = Field(
        ...,
        max_length=CAFE_ADDRESS_MAX_LENGTH,
    )
    phone: str = Field(
        ...,
        max_length=PHONE_MAX_LENGTH,
    )
    description: str = Field(
        ...,
        min_length=DESCRIPTION_MIN_LENGTH,
        max_length=DESCRIPTION_MAX_LENGTH,
    )
    photo_id: str | None = Field(
        default=None,
        max_length=UUID_LENGTH,
    )


class CafeCreate(CafeBase):
    """Создание кафе."""

    pass


class CafeUpdate(BaseSchema):
    """Частичное обновление кафе."""

    name: str | None = Field(
        default=None,
        min_length=CAFE_NAME_MIN_LENGTH,
        max_length=CAFE_NAME_MAX_LENGTH,
    )
    address: str | None = Field(
        default=None,
        max_length=CAFE_ADDRESS_MAX_LENGTH,
    )
    phone: str | None = Field(
        default=None,
        max_length=PHONE_MAX_LENGTH,
    )
    description: str | None = Field(
        default=None,
        min_length=DESCRIPTION_MIN_LENGTH,
        max_length=DESCRIPTION_MAX_LENGTH,
    )
    photo_id: str | None = Field(
        default=None,
        max_length=UUID_LENGTH,
    )
    is_active: bool | None = None


class CafeRead(CafeBase, UUIDIDSchema, TimestampSchema, ActiveSchema):
    """Полная схема кафе для ответа."""

    model_config = ConfigDict(from_attributes=True)


class CafeShort(UUIDIDSchema):
    """Краткая схема кафе для вложений."""

    name: str = Field(..., max_length=CAFE_NAME_MAX_LENGTH)
    address: str = Field(..., max_length=CAFE_ADDRESS_MAX_LENGTH)
