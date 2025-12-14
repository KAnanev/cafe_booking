from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.db import Base
from models.mixins import ActiveMixin, TimestampMixin


class CafeTable(TimestampMixin, ActiveMixin, Base):
    """Модель столов в кафе."""

    __tablename__ = 'tables'
    __table_args__ = (
        CheckConstraint(
            'seat_number > 0',
            name='ck_tables_seat_number_positive',
        ),
    )

    cafe_id = Column(
        UUID(as_uuid=True),
        ForeignKey('cafes.id', ondelete='CASCADE'),
        nullable=False,
    )
    seat_number = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)

    cafe = relationship('Cafe', back_populates='tables')
    booking_links = relationship(
        'BookingTableSlot',
        back_populates='table',
        cascade='all, delete-orphan',
    )
