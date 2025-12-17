from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.constants import (
    CAFE_ADDRESS_MAX_LENGTH,
    CAFE_NAME_MAX_LENGTH,
    DESCRIPTION_MAX_LENGTH,
    PHONE_MAX_LENGTH,
    UUID_LENGTH,
)
from core.db import Base
from models.mixins import ActiveMixin, TimestampMixin

if TYPE_CHECKING:
    from .slots import Slot
    from .table import Table
    from .user import User


class Cafe(TimestampMixin, ActiveMixin, Base):
    """Модель кафе."""

    __tablename__ = 'cafes'

    name: Mapped[str] = mapped_column(
        String(CAFE_NAME_MAX_LENGTH),
        nullable=False,
    )
    address: Mapped[str] = mapped_column(
        String(CAFE_ADDRESS_MAX_LENGTH),
        nullable=False,
    )
    phone: Mapped[str] = mapped_column(
        String(PHONE_MAX_LENGTH),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        String(DESCRIPTION_MAX_LENGTH),
        nullable=False,
    )
    photo_id: Mapped[str | None] = mapped_column(
        String(UUID_LENGTH),
        nullable=True,
    )

    managers: Mapped[list['User']] = relationship(
        'User',
        secondary='cafe_managers',
        back_populates='cafes',
        lazy='selectin',
    )

    tables: Mapped[list['Table']] = relationship(
        'Table',
        back_populates='cafe',
        cascade='all, delete-orphan',
        lazy='selectin',
    )
    slots: Mapped[list['Slot']] = relationship(
        'Slot',
        back_populates='cafe',
        cascade='all, delete-orphan',
        lazy='selectin',
    )

    def __str__(self) -> str:
        return f'{self.name} - {self.address}'
