import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db import Base

if TYPE_CHECKING:
    from models.booking import Booking
    from models.slot import Slot
    from models.table import Table


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

    booking_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('booking.id', ondelete='RESTRICT'),
        nullable=False,
        index=True,
    )
    table_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('table.id', ondelete='RESTRICT'),
        nullable=False,
        index=True,
    )
    slot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('slot.id', ondelete='RESTRICT'),
        nullable=False,
        index=True,
    )

    booking: Mapped['Booking'] = relationship(
        'Booking',
        lazy='selectin',
        back_populates='tables_slots',
    )
    table: Mapped['Table'] = relationship(lazy='selectin')
    slot: Mapped['Slot'] = relationship(lazy='selectin')
