# models/dishes.py
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.constants import DISH_DESCRIPTION_MAX_LENGTH, DISH_NAME_MAX_LENGTH
from core.db import Base
from models.mixins import ActiveMixin, TimestampMixin

if TYPE_CHECKING:
    from models.cafe import Cafe


class DishCafeLink(Base):
    """Связующая таблица (Many-to-Many) между блюдами и кафе."""

    __tablename__ = 'dish_cafe_link'

    dish_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('dishes.id', ondelete='CASCADE'),
        primary_key=True,
    )
    cafe_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('cafes.id', ondelete='CASCADE'),
        primary_key=True,
    )

    cafe: Mapped['Cafe'] = relationship(lazy='selectin')


class Dish(TimestampMixin, ActiveMixin, Base):
    """Модель блюда в меню кафе."""

    __tablename__ = 'dishes'

    name: Mapped[str] = mapped_column(
        String(DISH_NAME_MAX_LENGTH),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        String(DISH_DESCRIPTION_MAX_LENGTH),
        nullable=True,
    )
    photo_id: Mapped[str | None] = mapped_column(
        nullable=True,
    )
    price: Mapped[float] = mapped_column(
        Numeric(10, 2),
        CheckConstraint('price >= 0'),
        nullable=False,
    )

    # cafes: Mapped[List['Cafe']] = relationship(
    #     'Cafe',
    #     secondary=DishCafeLink.__table__,
    #     back_populates='dishes',
    #     lazy='selectin',
    # )

    def __str__(self) -> str:
        return f'{self.name} ({self.price} у.е.)'
