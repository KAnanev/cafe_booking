from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from core.db import Base
from models.mixins import ActiveMixin, TimestampMixin


class Image(TimestampMixin, ActiveMixin, Base):
    """Модель для хранения метаданных изображений в системы."""

    file_path: Mapped[str] = mapped_column(
        String(),
        nullable=False,
    )

    def __str__(self) -> str:
        return self.file_path
