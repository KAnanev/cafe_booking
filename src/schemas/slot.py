from __future__ import annotations

from datetime import time

from pydantic import Field, model_validator

from schemas.base import (
    ActiveSchema,
    BaseSchema,
    TimestampSchema,
    UUIDIDSchema,
)
from schemas.cafe import CafeShortInfo


class TimeSlotCreate(BaseSchema):
    """Данные для создания временного слота."""

    start_time: time
    end_time: time
    description: str | None = None

    @model_validator(mode="after")
    def validate_time_order(self) -> "TimeSlotCreate":
        """Убедиться, что начало слота раньше окончания."""
        if self.start_time >= self.end_time:
            msg = "Время начала слота должно быть раньше окончания."
            raise ValueError(msg)
        return self


class TimeSlotUpdate(BaseSchema):
    """Данные для обновления временного слота."""

    start_time: time | None = Field(None)
    end_time: time | None = Field(None)
    description: str | None = None
    is_active: bool | None = None

    @model_validator(mode="after")
    def validate_time_pair(self) -> "TimeSlotUpdate":
        """Изменение времени требует оба поля и корректный порядок."""
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                msg = "Время начала слота должно быть раньше окончания."
                raise ValueError(msg)
        return self


class TimeSlotShortInfo(UUIDIDSchema, BaseSchema):
    """Краткая информация о временном слоте."""

    start_time: time
    end_time: time
    description: str | None = None


class TimeSlotInfo(UUIDIDSchema, TimestampSchema, ActiveSchema, BaseSchema):
    """Полная информация о временном слоте."""

    cafe: CafeShortInfo
    start_time: time
    end_time: time
    description: str | None = None
