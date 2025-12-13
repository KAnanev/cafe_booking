from datetime import time
from typing import Any
from uuid import UUID

from pydantic import ConfigDict, Field, model_validator

from core.constant import DESCRIPTION_MAX_LENGTH, DESCRIPTION_MIN_LENGTH
from schemas.base import (
    ActiveSchema, BaseSchema, TimestampSchema, UUIDIDSchema
)
from schemas.cafe import CafeShort


class TimeSlotShort(BaseSchema):
    """Краткая информация о слоте."""

    id: int | None = None
    start_time: time
    end_time: time
    description: str = Field(
        ...,
        max_length=DESCRIPTION_MAX_LENGTH,
    )

    model_config = ConfigDict(from_attributes=True)


class SlotBase(BaseSchema):
    """Общие поля слота."""

    start_time: time
    end_time: time
    description: str | None = Field(
        default=None,
        max_length=DESCRIPTION_MAX_LENGTH,
        min_length=DESCRIPTION_MIN_LENGTH,
    )

    @model_validator(mode='before')
    def check_times(cls, values: dict[str, Any]) -> dict[str, Any]:
        start = values.get('start_time')
        end = values.get('end_time')
        if start and end and start >= end:
            raise ValueError(
                'Начальное время не может быть больше или равно конечному',
            )
        return values


class SlotCreate(SlotBase):
    """Создание слота."""

    cafe_id: UUID


class SlotUpdate(BaseSchema):
    """Частичное обновление слота."""

    cafe_id: UUID | None = None
    start_time: time | None = None
    end_time: time | None = None
    is_active: bool | None = None
    description: str | None = Field(
        default=None,
        max_length=DESCRIPTION_MAX_LENGTH,
        min_length=DESCRIPTION_MIN_LENGTH,
    )

    @model_validator(mode='before')
    def check_times(cls, values: dict[str, Any]) -> dict[str, Any]:
        start = values.get('start_time')
        end = values.get('end_time')
        if start and end and start >= end:
            raise ValueError(
                'Начальное время не может быть больше или равно конечному',
            )
        return values


class SlotRead(SlotBase, UUIDIDSchema, TimestampSchema, ActiveSchema):
    """Полное представление слота."""

    cafe: CafeShort
    model_config = ConfigDict(from_attributes=True)
