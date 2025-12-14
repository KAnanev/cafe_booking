from datetime import time

from schemas.base import BaseSchema, UUIDIDSchema


class TimeSlotShortInfo(UUIDIDSchema, BaseSchema):
    """Cхема с краткой информацией о слоте времени."""

    start_time: time
    end_time: time
    description: str | None = None
