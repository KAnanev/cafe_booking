from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.constants import (
    CAFE_ADDRESS_MAX_LENGTH,
    CAFE_NAME_MAX_LENGTH,
    DESCRIPTION_MAX_LENGTH,
    PHONE_MAX_LENGTH,
)
from core.db import Base
from models.mixins import ActiveMixin, TimestampMixin

if TYPE_CHECKING:
    from models.booking import Booking
    from models.slots import Slot
    from models.table import Table
    from models.user import User


class Cafe(TimestampMixin, ActiveMixin, Base):
    """Модель кафе."""

    __tablename__ = 'cafes'
    __table_args__ = (
        UniqueConstraint('name', 'address', name='uq_cafes_name_address'),
    )

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
    photo_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
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
    bookings: Mapped[list['Booking']] = relationship(
        'Booking',
        back_populates='cafe',
        cascade='all, delete-orphan',
        lazy='selectin',
    )

    def __str__(self) -> str:
        return f'{self.name} - {self.address}'
