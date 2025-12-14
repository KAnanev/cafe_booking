import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.constant import (
    TABLE_DESCRIPTION_MAX_LENGTH,
    TABLE_MAX_SEATS_NUMBER,
    TABLE_MIN_SEATS_NUMBER,
)
from core.db import Base
from models.mixins import ActiveMixin, TimestampMixin

if TYPE_CHECKING:
    from .cafe import Cafe


class Table(TimestampMixin, ActiveMixin, Base):
    """Модель стола в кафе."""

    __tablename__ = 'tables'
    __table_args__ = (
        CheckConstraint(
            f'seats_number >= {TABLE_MIN_SEATS_NUMBER}',
            name='check_min_seats',
        ),
        CheckConstraint(
            f'seats_number <= {TABLE_MAX_SEATS_NUMBER}',
            name='check_max_seats',
        ),
    )

    cafe_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('cafes.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    seats_number: Mapped[int] = mapped_column(
        Integer(),
        nullable=False,
        index=True,
    )
    description: Mapped[Optional[str]] = mapped_column(
        String(TABLE_DESCRIPTION_MAX_LENGTH),
        nullable=True,
    )

    cafe: Mapped['Cafe'] = relationship(
        'Cafe',
        back_populates='tables',
        lazy='selectin',
    )
