import uuid
from datetime import date
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Date,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db import Base
from models.mixins import ActiveMixin, TimestampMixin

if TYPE_CHECKING:
    from models.booking_table_slot import BookingTableSlot
    from models.cafe import Cafe
    from models.user import User


class BookingStatus(StrEnum):
    """Статусы бронирования столов."""

    BOOKING = 'BOOKING'
    ACTIVE = 'ACTIVE'
    CANCELED = 'CANCELED'


class Booking(TimestampMixin, ActiveMixin, Base):
    """Модель бронирования столов в кафе."""

    __table_args__ = (
        CheckConstraint(
            'guest_number > 0',
            name='ck_booking_guest_number_positive',
        ),
        Index('ix_bookings_cafe_date', 'cafe_id', 'booking_date'),
        Index(
            'ix_bookings_cafe_date_status',
            'cafe_id',
            'booking_date',
            'status',
        ),
        Index('ix_bookings_user_date', 'user_id', 'booking_date'),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('user.id', ondelete='RESTRICT'),
        nullable=False,
        index=True,
    )
    cafe_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('cafe.id', ondelete='RESTRICT'),
        nullable=False,
        index=True,
    )

    guest_number: Mapped[int] = mapped_column(Integer, nullable=False)

    note: Mapped[str | None] = mapped_column(Text, nullable=False)

    status: Mapped['BookingStatus'] = mapped_column(
        Enum(BookingStatus, name='booking_status'),
        nullable=False,
        server_default=text(f"'{BookingStatus.BOOKING.value}'"),
    )
    booking_date: Mapped[date] = mapped_column(Date, nullable=False)

    user: Mapped['User'] = relationship('User', lazy='selectin')
    cafe: Mapped['Cafe'] = relationship('Cafe', lazy='selectin')

    tables_slots: Mapped[list['BookingTableSlot']] = relationship(
        'BookingTableSlot',
        lazy='selectin',
    )
