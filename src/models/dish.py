import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.constants import DISH_DESCRIPTION_MAX_LENGTH, DISH_NAME_MAX_LENGTH
from core.db import Base
from models.mixins import ActiveMixin, TimestampMixin

if TYPE_CHECKING:
    from models.cafe import Cafe


class DishCafeLink(TimestampMixin, ActiveMixin, Base):
    """Связующая таблица (Many-to-Many) между блюдами и кафе."""

    __table_args__ = (
        UniqueConstraint('dish_id', 'cafe_id', name='uq_dish_cafe'),
    )

    dish_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('dish.id', ondelete='RESTRICT'),
        nullable=False,
        index=True,
    )
    cafe_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('cafe.id', ondelete='RESTRICT'),
        nullable=False,
        index=True,
    )

    dish: Mapped['Dish'] = relationship(
        'Dish',
        back_populates='cafe_links',
        lazy='selectin',
    )
    cafe: Mapped['Cafe'] = relationship(
        'Cafe',
        lazy='selectin',
    )


class Dish(TimestampMixin, ActiveMixin, Base):
    """Модель блюда в меню кафе."""

    name: Mapped[str] = mapped_column(
        String(DISH_NAME_MAX_LENGTH),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        String(DISH_DESCRIPTION_MAX_LENGTH),
        nullable=True,
    )
    photo_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    cafe_links: Mapped[list['DishCafeLink']] = relationship(
        'DishCafeLink',
        back_populates='dish',
        lazy='selectin',
    )

    __table_args__ = (
        CheckConstraint('price >= 0', name='ck_dishes_price_non_negative'),
    )

    def __str__(self) -> str:
        return f'{self.name} ({self.price} у.е.)'
