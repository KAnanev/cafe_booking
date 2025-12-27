from enum import StrEnum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, CheckConstraint, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.constants import (
    CHECK_USER_EMAIL_OR_PHONE,
    EMAIL_MAX_LENGTH,
    PASSWORD_HASH_MAX_LENGTH,
    PHONE_MAX_LENGTH,
    ROLE_ADMIN,
    ROLE_MANAGER,
    ROLE_USER,
    TG_ID_MAX_LENGTH,
    USERNAME_MAX_LENGTH,
)
from core.db import Base
from models.mixins import ActiveMixin, TimestampMixin

if TYPE_CHECKING:
    from models.cafe import Cafe
    from models.user_session import UserSession


class UserRole(StrEnum):
    """Роли пользователя."""

    USER = ROLE_USER
    MANAGER = ROLE_MANAGER
    ADMIN = ROLE_ADMIN


class User(TimestampMixin, ActiveMixin, Base):
    """Модель пользователя."""

    __table_args__ = (
        CheckConstraint(
            'email IS NOT NULL OR phone IS NOT NULL',
            name=CHECK_USER_EMAIL_OR_PHONE,
        ),
    )

    username: Mapped[str] = mapped_column(
        String(USERNAME_MAX_LENGTH),
        unique=True,
        index=True,
        nullable=False,
    )

    email: Mapped[Optional[str]] = mapped_column(
        String(EMAIL_MAX_LENGTH),
        unique=True,
        index=True,
        nullable=True,
    )

    phone: Mapped[Optional[str]] = mapped_column(
        String(PHONE_MAX_LENGTH),
        unique=True,
        index=True,
        nullable=True,
    )

    tg_id: Mapped[Optional[str]] = mapped_column(
        String(TG_ID_MAX_LENGTH),
        unique=True,
        index=True,
        nullable=True,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(PASSWORD_HASH_MAX_LENGTH),
        nullable=False,
    )

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name='user_role'),
        default=UserRole.USER,
        nullable=False,
    )

    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    sessions: Mapped[list['UserSession']] = relationship(
        back_populates='user',
    )

    cafes: Mapped[list['Cafe']] = relationship(
        'Cafe',
        secondary='cafe_managers',
        back_populates='managers',
        lazy='noload',  # Чтобы не грузилось для системных операций init_db
    )
