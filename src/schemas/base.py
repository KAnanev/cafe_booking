from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Базовая схема для всех моделей."""

    model_config = ConfigDict(from_attributes=True)


class TimestampSchema(BaseSchema):
    """Схема с временными метками."""

    created_at: datetime
    updated_at: datetime | None = None


class ActiveSchema(BaseSchema):
    """Схема с полем активности."""

    is_active: bool = True


class UUIDIDSchema(BaseSchema):
    """Схема с UUID ID."""

    id: UUID
