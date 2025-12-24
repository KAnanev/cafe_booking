from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db import Base


class BookingTableSlot(Base):
    """Связка бронирования с конкретным столом и временным слотом."""

    __table_args__ = (
        UniqueConstraint(
            'booking_id',
            'table_id',
            'slot_id',
            name='uq_booking_table_slot',
        ),
    )

    booking_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('booking.id'),
        nullable=False,
    )
    table_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('table.id'),
        nullable=False,
    )
    slot_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('slot.id'),
        nullable=False,
    )

    booking: Mapped['Booking'] = relationship(back_populates='tables_slots')
    table: Mapped['Table'] = relationship(back_populates='booking_links')
    slot: Mapped['Slot'] = relationship(back_populates='booking_links')
