from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4


@dataclass(kw_only=True)
class BaseEntity:
    """Базовый класс сущности с общими атрибутами."""

    id: UUID = field(default_factory=uuid4)
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def touch(self) -> None:
        """Обновляет атрибут времени последнего обновления объекта."""
        self.updated_at = datetime.now(UTC)

    def deactivate(self) -> None:
        """Останавливает активность объекта."""
        self.is_active = False
        self.touch()
