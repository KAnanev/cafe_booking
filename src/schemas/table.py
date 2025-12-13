from uuid import UUID

from pydantic import ConfigDict, Field

from core.constant import (
    TABLE_DESCRIPTION_MAX_LENGTH,
    TABLE_MAX_SEATS_NUMBER,
    TABLE_MIN_SEATS_NUMBER,
)
from schemas.base import (
    ActiveSchema,
    BaseSchema,
    TimestampSchema,
    UUIDIDSchema,
)
from schemas.cafe import CafeShort


class TableBase(BaseSchema):
    """Базовые поля стола."""

    seats_number: int = Field(
        ...,
        ge=TABLE_MIN_SEATS_NUMBER,
        le=TABLE_MAX_SEATS_NUMBER,
    )
    description: str | None = Field(
        default=None,
        max_length=TABLE_DESCRIPTION_MAX_LENGTH,
    )


class TableCreate(TableBase):
    """Создание стола."""

    cafe_id: UUID


class TableUpdate(BaseSchema):
    """Частичное обновление стола."""

    cafe_id: UUID | None = None
    seats_number: int | None = Field(
        default=None,
        ge=TABLE_MIN_SEATS_NUMBER,
        le=TABLE_MAX_SEATS_NUMBER,
    )
    description: str | None = Field(
        default=None,
        max_length=TABLE_DESCRIPTION_MAX_LENGTH,
    )
    is_active: bool | None = None


class TableRead(TableBase, UUIDIDSchema, TimestampSchema, ActiveSchema):
    """Полная схема стола с вложенным кафе."""

    cafe: CafeShort
    model_config = ConfigDict(from_attributes=True)


class TableShort(UUIDIDSchema):
    """Краткая схема стола."""

    seats_number: int
    description: str | None = Field(
        default=None,
        max_length=TABLE_DESCRIPTION_MAX_LENGTH,
    )

    model_config = ConfigDict(from_attributes=True)
