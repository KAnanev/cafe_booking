from __future__ import annotations

from pydantic import Field

from schemas.base import (
    ActiveSchema,
    BaseSchema,
    TimestampSchema,
    UUIDIDSchema,
)
from schemas.cafe import CafeShortInfo


class TableCreate(BaseSchema):
    """Данные для создания стола."""

    description: str | None = None
    seat_number: int = Field(..., gt=0)


class TableUpdate(BaseSchema):
    """Данные для обновления стола."""

    description: str | None = None
    seat_number: int | None = Field(None, gt=0)
    is_active: bool | None = None


class TableShortInfo(UUIDIDSchema, BaseSchema):
    """Краткая информация о столе."""

    description: str | None = None
    seat_number: int


class TableInfo(UUIDIDSchema, TimestampSchema, ActiveSchema, BaseSchema):
    """Полная информация о столе."""

    cafe: CafeShortInfo
    description: str | None = None
    seat_number: int
