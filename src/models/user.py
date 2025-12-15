from enum import IntEnum
from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.constants import ROLE_ADMIN, ROLE_MANAGER, ROLE_USER
from core.db import Base
from models.mixins import ActiveMixin, TimestampMixin

if TYPE_CHECKING:
    from .cafe import Cafe


class Roles(IntEnum):
    """Роли пользователя."""

    USER = ROLE_USER
    MANAGER = ROLE_MANAGER
    ADMIN = ROLE_ADMIN


class User(TimestampMixin, ActiveMixin, Base):
    """Модель пользователя."""

    __tablename__ = 'users'

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    role: Mapped[Roles] = mapped_column(
        Integer,
        default=Roles.USER,
        nullable=False,
    )

    cafes: Mapped[list['Cafe']] = relationship(
        'Cafe',
        secondary='cafe_managers',
        back_populates='managers',
        lazy='selectin',
    )

    def __str__(self) -> str:
        return f'{self.email} (role={self.role.name})'

    def __repr__(self) -> str:
        return f'<User({self.id}, email={self.email}, role={self.role.name})>'
