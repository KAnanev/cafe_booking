from __future__ import annotations

from uuid import UUID

from pydantic import Field

from core.constant import NAME_MAX_LENGTH
from schemas.base import (
    ActiveSchema,
    BaseSchema,
    TimestampSchema,
    UUIDIDSchema,
)
from schemas.user import UserShortInfo


class CafeBase(BaseSchema):
    """Базовая схема кафе."""

    name: str = Field(..., max_length=NAME_MAX_LENGTH)
    address: str
    phone: str
    description: str | None = None
    photo_id: UUID


class CafeCreate(CafeBase):
    """Схема создания кафе."""

    managers_id: list[UUID]


class CafeUpdate(BaseSchema):
    """Схема обновления кафе."""

    name: str | None = Field(None, max_length=NAME_MAX_LENGTH)
    address: str | None = None
    phone: str | None = None
    description: str | None = None
    photo_id: UUID | None = None
    managers_id: list[UUID] | None = None
    is_active: bool | None = None


class CafeShortInfo(UUIDIDSchema, BaseSchema):
    """Короткая информация о кафе."""

    name: str
    address: str
    phone: str
    description: str | None = None
    photo_id: UUID


class CafeInfo(UUIDIDSchema, TimestampSchema, ActiveSchema, CafeBase):
    """Полная информация о кафе."""

    managers: list["UserShortInfo"] = []
