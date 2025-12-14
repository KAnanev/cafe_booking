from sqlalchemy import ARRAY, Column, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.constant import NAME_MAX_LENGTH
from core.db import Base
from models.mixins import ActiveMixin, TimestampMixin


class Cafe(TimestampMixin, ActiveMixin, Base):
    """Модель кафе."""

    __tablename__ = 'cafes'

    name = Column(String(NAME_MAX_LENGTH), nullable=False)
    address = Column(String(255), nullable=False)
    phone = Column(String(32), nullable=False)
    description = Column(Text, nullable=True)
    photo_id = Column(UUID(as_uuid=True), nullable=False)
    managers_id = Column(
        ARRAY(UUID(as_uuid=True)),
        nullable=False,
        default=list,
    )

    tables = relationship(
        'CafeTable',
        back_populates='cafe',
        cascade='all, delete-orphan',
    )
    slots = relationship(
        'TimeSlot',
        back_populates='cafe',
        cascade='all, delete-orphan',
    )
    bookings = relationship('Booking', back_populates='cafe')
