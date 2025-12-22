import uuid
from datetime import time
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.constants import DESCRIPTION_MAX_LENGTH
from core.db import Base
from models.mixins import ActiveMixin, TimestampMixin

if TYPE_CHECKING:
    from models.booking_table_slot import BookingTableSlot
    from models.cafe import Cafe


class Slot(TimestampMixin, ActiveMixin, Base):
    """Временной слот для бронирования в кафе."""

    __table_args__ = (
        CheckConstraint(
            'end_time > start_time',
            name='ck_slots_end_time_gt_start_time',
        ),
    )

    cafe_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('cafes.id', ondelete='CASCADE'),
        nullable=False,
    )
    start_time: Mapped[time] = mapped_column(nullable=False)
    end_time: Mapped[time] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(
        String(DESCRIPTION_MAX_LENGTH),
        nullable=True,
        default=None,
    )

    cafe: Mapped['Cafe'] = relationship(
        'Cafe',
        back_populates='slots',
        lazy='selectin',
    )

    booking_links: Mapped[list['BookingTableSlot']] = relationship(
        'BookingTableSlot',
        back_populates='slot',
        cascade='all, delete-orphan',
        lazy='selectin',
    )
