from typing import List, Optional
from uuid import UUID

from pydantic import ConfigDict, Field

from core.constants import (
    DISH_DESCRIPTION_MAX_LENGTH,
    DISH_NAME_MAX_LENGTH,
    DISH_NAME_MIN_LENGTH,
    UUID_LENGTH,
)
from schemas.base import (
    ActiveSchema,
    BaseSchema,
    TimestampSchema,
    UUIDIDSchema,
)
from schemas.cafe import CafeShort


class DishBase(BaseSchema):
    """Базовая схема для блюд."""

    name: str = Field(
        ...,
        min_length=DISH_NAME_MIN_LENGTH,
        max_length=DISH_NAME_MAX_LENGTH,
    )
    description: Optional[str] = Field(
        default=None,
        max_length=DISH_DESCRIPTION_MAX_LENGTH,
    )
    photo_id: Optional[str] = Field(default=None, max_length=UUID_LENGTH)
    price: float = Field(..., gt=0)


class DishCreate(DishBase):
    """Схема для создания блюда."""

    cafes_id: List[UUID]


class DishUpdate(BaseSchema):
    """Схема для частичного обновления данных блюда."""

    name: Optional[str] = Field(
        default=None,
        min_length=DISH_NAME_MIN_LENGTH,
        max_length=DISH_NAME_MAX_LENGTH,
    )
    description: Optional[str] = Field(
        default=None,
        max_length=DISH_DESCRIPTION_MAX_LENGTH,
    )
    photo_id: Optional[str] = Field(default=None, max_length=UUID_LENGTH)
    price: Optional[float] = Field(default=None, gt=0)
    cafes_id: Optional[List[UUID]] = None
    is_active: Optional[bool] = None


class DishRead(UUIDIDSchema, TimestampSchema, ActiveSchema, BaseSchema):
    """Схема для чтения данных блюда."""

    id: UUID
    name: str
    description: Optional[str]
    photo_id: Optional[str]
    price: float
    cafes: List[CafeShort]

    model_config = ConfigDict(from_attributes=True)
