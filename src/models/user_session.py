import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db import Base
from models.user import User

from .mixins import ActiveMixin, TimestampMixin

if TYPE_CHECKING:
    from .user import User


class UserSession(ActiveMixin, TimestampMixin, Base):
    """Модель сессии."""

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f'{User.__tablename__}.id'),
        nullable=False,
    )
    last_activity: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    user: Mapped[User] = relationship(back_populates='sessions')

    __table_args__ = (
        Index('ix_user_sessions_user_id', 'user_id'),
        Index('ix_user_sessions_expires_at', 'expires_at'),
    )
