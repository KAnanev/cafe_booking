# from typing import TYPE_CHECKING
# import uuid

# from sqlalchemy import String
# from sqlalchemy.dialects.postgresql import UUID
# from sqlalchemy.orm import Mapped, mapped_column

# from core.db import Base
# from models.mixins import TimestampMixin, ActiveMixin


# class Image(TimestampMixin, ActiveMixin, Base):
#     __tablename__ = "images"

#     id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         primary_key=True,
#     )

#     file_path: Mapped[str] = mapped_column(
#         String(),
#         nullable=False,
#     )

#     def __str__(self) -> str:
#         return self.file_path


import uuid

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.db import Base


class Image(Base):
    """Модель для хранения метаданных изображений в системе."""

    __tablename__ = 'images'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    file_path: Mapped[str] = mapped_column(
        String(),
        nullable=False,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __str__(self) -> str:
        return self.file_path
