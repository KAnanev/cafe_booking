import enum

from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    ForeignKey,
    Integer,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.db import Base
from models.mixins import ActiveMixin, TimestampMixin


class BookingStatus(int, enum.Enum):
    """Статусы бронирования столов."""

    BOOKING = 0
    CANCELED = 1
    ACTIVE = 2


class Booking(TimestampMixin, ActiveMixin, Base):
    """Модель бронирования столов в кафе."""

    __tablename__ = 'bookings'

    user_id = Column(UUID(as_uuid=True), nullable=True)
    cafe_id = Column(
        UUID(as_uuid=True),
        ForeignKey('cafes.id', ondelete='CASCADE'),
        nullable=False,
    )
    guest_number = Column(
        Integer,
        CheckConstraint('guest_number > 0', name='ck_guest_number_positive'),
        nullable=False,
    )
    note = Column(Text, nullable=True)
    status = Column(
        Integer,
        nullable=False,
        default=BookingStatus.BOOKING.value,
        server_default=text('0'),
    )
    booking_date = Column(Date, nullable=False)

    cafe = relationship('Cafe', back_populates='bookings')
    tables_slots = relationship(
        'BookingTableSlot',
        back_populates='booking',
        cascade='all, delete-orphan',
    )
