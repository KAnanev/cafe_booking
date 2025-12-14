from uuid import UUID

from schemas.base import BaseSchema, UUIDIDSchema


class CafeShortInfo(UUIDIDSchema, BaseSchema):
    """Схема с краткой информацией о кафе."""

    name: str
    address: str
    phone: str
    description: str | None = None
    photo_id: UUID
