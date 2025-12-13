from datetime import time
from typing import TYPE_CHECKING
import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as UUIDType
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.constant import DESCRIPTION_MAX_LENGTH
from core.db import Base
from models.mixins import ActiveMixin, TimestampMixin

if TYPE_CHECKING:
    from .cafe import Cafe


class Slot(TimestampMixin, ActiveMixin, Base):
    """Временной слот для бронирования в кафе."""

    __tablename__ = 'slots'

    cafe_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(as_uuid=True),
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
