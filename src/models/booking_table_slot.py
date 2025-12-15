from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.db import Base


class BookingTableSlot(Base):
    """Связка бронирования с конкретным столом и временным слотом."""

    __tablename__ = 'booking_table_slots'
    __table_args__ = (
        UniqueConstraint(
            'booking_id',
            'table_id',
            'slot_id',
            name='uq_booking_table_slot',
        ),
    )

    booking_id = Column(
        UUID(as_uuid=True),
        ForeignKey('bookings.id', ondelete='CASCADE'),
        nullable=False,
    )
    table_id = Column(
        UUID(as_uuid=True),
        ForeignKey('tables.id', ondelete='CASCADE'),
        nullable=False,
    )
    slot_id = Column(
        UUID(as_uuid=True),
        ForeignKey('slots.id', ondelete='CASCADE'),
        nullable=False,
    )

    booking = relationship('Booking', back_populates='tables_slots')
    table = relationship('Table', back_populates='booking_links')
    slot = relationship('Slot', back_populates='booking_links')
