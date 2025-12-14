from sqlalchemy import CheckConstraint, Column, ForeignKey, Text, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.db import Base
from models.mixins import ActiveMixin, TimestampMixin


class TimeSlot(TimestampMixin, ActiveMixin, Base):
    """Модель временных слотов для бронирования."""

    __tablename__ = "time_slots"
    __table_args__ = (
        CheckConstraint("start_time < end_time", name="ck_slots_time_order"),
    )

    cafe_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cafes.id", ondelete="CASCADE"),
        nullable=False,
    )
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    description = Column(Text, nullable=True)

    cafe = relationship("Cafe", back_populates="slots")
    booking_links = relationship(
        "BookingTableSlot",
        back_populates="slot",
        cascade="all, delete-orphan",
    )
