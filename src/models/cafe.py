import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.constants import (
    CAFE_ADDRESS_MAX_LENGTH,
    CAFE_NAME_MAX_LENGTH,
    DESCRIPTION_MAX_LENGTH,
    PHONE_MAX_LENGTH,
)
from core.db import Base
from models.mixins import ActiveMixin, TimestampMixin

if TYPE_CHECKING:
    from models.user import User


class CafeManagerLink(TimestampMixin, ActiveMixin, Base):
    """Связь User ↔ Cafe для менеджеров."""

    cafe_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('cafe.id', ondelete='RESTRICT'),
        nullable=False,
        index=True,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('user.id', ondelete='RESTRICT'),
        nullable=False,
        index=True,
    )

    cafe: Mapped['Cafe'] = relationship(
        'Cafe',
        back_populates='manager_links',
        lazy='selectin',
    )
    user: Mapped['User'] = relationship('User', lazy='selectin')

    __table_args__ = (
        Index(
            'uq_cafe_managers_active',
            'cafe_id',
            'user_id',
            unique=True,
            postgresql_where=text('is_active IS TRUE'),
        ),
    )


class Cafe(TimestampMixin, ActiveMixin, Base):
    """Модель кафе."""

    __table_args__ = (
        UniqueConstraint('name', 'address', name='uq_cafes_name_address'),
    )

    name: Mapped[str] = mapped_column(
        String(CAFE_NAME_MAX_LENGTH),
        nullable=False,
    )
    address: Mapped[str] = mapped_column(
        String(CAFE_ADDRESS_MAX_LENGTH),
        nullable=False,
    )
    phone: Mapped[str] = mapped_column(
        String(PHONE_MAX_LENGTH),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        String(DESCRIPTION_MAX_LENGTH),
        nullable=True,
    )
    photo_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    manager_links: Mapped[list['CafeManagerLink']] = relationship(
        'CafeManagerLink',
        back_populates='cafe',
        lazy='selectin',
    )

    def __str__(self) -> str:
        return f'{self.name} - {self.address}'

    @property
    def managers(self) -> list['User']:
        """Возвращает менеджеров."""
        return [
            link.user
            for link in self.manager_links
            if link.is_active
            and link.user is not None
            and getattr(link.user, 'is_active', True)
        ]
