from abc import ABC, abstractmethod

from auth.domain.permissions.context import UserContext


class PermissionPolicy(ABC):
    """Контракт для политики разрешений."""

    @abstractmethod
    def is_allowed(self, *, user: UserContext | None, action: str) -> bool:
        """Проверяет, разрешено ли действие для пользователя."""
        ...
