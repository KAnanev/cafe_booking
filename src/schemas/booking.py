from __future__ import annotations

from datetime import date
from uuid import UUID

from pydantic import Field, field_validator

from models.booking import BookingStatus
from schemas.base import (
    ActiveSchema,
    BaseSchema,
    TimestampSchema,
    UUIDIDSchema,
)
from schemas.cafe import CafeShortInfo
from schemas.slot import TimeSlotShortInfo
from schemas.table import TableShortInfo
from schemas.user import UserShortInfo


class TablesSlots(BaseSchema):
    """Связка стол/слот для запроса."""

    table_id: UUID
    slot_id: UUID


class TablesSlotsInfo(UUIDIDSchema, BaseSchema):
    """Связка стол/слот для ответа."""

    table: TableShortInfo
    slot: TimeSlotShortInfo


class BookingCreate(BaseSchema):
    """Создание бронирования."""

    cafe_id: UUID
    tables_slots: list[TablesSlots]
    guest_number: int = Field(..., gt=0)
    note: str | None = None
    status: BookingStatus
    booking_date: date

    @field_validator("booking_date")
    @classmethod
    def validate_booking_date(cls, value: date) -> date:
        """Нельзя бронировать прошлое."""
        if value < date.today():
            msg = "Нельзя бронировать прошедшую дату."
            raise ValueError(msg)
        return value

    @field_validator("tables_slots")
    @classmethod
    def validate_tables_slots(
        cls,
        value: list[TablesSlots],
    ) -> list[TablesSlots]:
        """Должна быть указана хотя бы одна пара стол/слот."""
        if not value:
            msg = "Нужно указать хотя бы одну пару стол/слот."
            raise ValueError(msg)
        return value


class BookingInfo(UUIDIDSchema, TimestampSchema, ActiveSchema, BaseSchema):
    """Ответ по бронированию."""

    user: UserShortInfo | None = None
    cafe: CafeShortInfo
    tables_slots: list[TablesSlotsInfo]
    guest_number: int
    note: str | None = None
    status: BookingStatus
    booking_date: date
