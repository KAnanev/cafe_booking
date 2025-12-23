from sqlalchemy import Column, ForeignKey, Table, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from core.db import Base

cafe_managers = Table(
    'cafe_managers',
    Base.metadata,
    Column(
        'cafe_id',
        UUID(as_uuid=True),
        ForeignKey('cafes.id', ondelete='RESTRICT'),
        nullable=False,
        index=True,
    ),
    Column(
        'user_id',
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='RESTRICT'),
        primary_key=True,
        nullable=False,
    ),
    UniqueConstraint('user_id', name='uq_cafe_managers_user_id'),
)
