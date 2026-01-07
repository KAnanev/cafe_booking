import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.constants import (
    TABLE_DESCRIPTION_MAX_LENGTH,
    TABLE_MAX_SEAT_NUMBER,
    TABLE_MIN_SEAT_NUMBER,
)
from core.db import Base
from models.mixins import ActiveMixin, TimestampMixin

if TYPE_CHECKING:
    from models.cafe import Cafe


class Table(TimestampMixin, ActiveMixin, Base):
    """Модель стола в кафе."""

    __table_args__ = (
        CheckConstraint(
            (
                f'seat_number BETWEEN {TABLE_MIN_SEAT_NUMBER} '
                f'AND {TABLE_MAX_SEAT_NUMBER}'
            ),
            name='check_seat_number_range',
        ),
    )

    cafe_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('cafe.id', ondelete='RESTRICT'),
        nullable=False,
        index=True,
    )
    seat_number: Mapped[int] = mapped_column(
        Integer(),
        nullable=False,
        index=True,
    )
    description: Mapped[Optional[str]] = mapped_column(
        String(TABLE_DESCRIPTION_MAX_LENGTH),
        nullable=True,
    )

    cafe: Mapped['Cafe'] = relationship('Cafe', lazy='selectin')
