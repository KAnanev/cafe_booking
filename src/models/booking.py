from enum import StrEnum

from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    Enum,
    ForeignKey,
    Integer,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.db import Base
from models.mixins import ActiveMixin, TimestampMixin


class BookingStatus(StrEnum):
    """Статусы бронирования столов."""

    BOOKING = 'booking'
    CANCELED = 'canceled'
    ACTIVE = 'active'


class Booking(TimestampMixin, ActiveMixin, Base):
    """Модель бронирования столов в кафе."""

    user_id = Column(UUID(as_uuid=True), nullable=True)
    cafe_id = Column(
        UUID(as_uuid=True),
        ForeignKey('cafes.id'),
        nullable=False,
    )
    guest_number = Column(
        Integer,
        CheckConstraint('guest_number > 0', name='ck_guest_number_positive'),
        nullable=False,
    )
    note = Column(Text, nullable=True)
    status = Column(
        Enum(BookingStatus, name='booking_status'),
        nullable=False,
        default=BookingStatus.BOOKING,
    )
    booking_date = Column(Date, nullable=False)

    cafe = relationship('Cafe', back_populates='bookings')
    tables_slots = relationship(
        'BookingTableSlot',
        back_populates='booking',
    )
