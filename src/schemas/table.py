from schemas.base import BaseSchema, UUIDIDSchema


class TableShortInfo(UUIDIDSchema, BaseSchema):
    """Схема с краткой информацией о столе."""

    description: str | None = None
    seat_number: int
