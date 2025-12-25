import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db import Base
from models.user import User

if TYPE_CHECKING:
    from .user import User


class UserSession(Base):
    """Модель сессии."""

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f'{User.__tablename__}.id'),
    )
    last_activity: Mapped[datetime]
    expires_at: Mapped[datetime]

    user: Mapped[User] = relationship(back_populates='sessions')
