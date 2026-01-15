import uuid

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.db import Base
from models.mixins import ActiveMixin, TimestampMixin


class Image(TimestampMixin, ActiveMixin, Base):
    """Модель для хранения метаданных изображений в системы."""

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    file_path: Mapped[str] = mapped_column(
        String(),
        nullable=False,
    )

    def __str__(self) -> str:
        return self.file_path
