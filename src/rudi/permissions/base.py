from abc import ABC, abstractmethod

from accounts.auth import UserContext


class PermissionPolicy(ABC):
    """Контракт для политики разрешений."""

    @abstractmethod
    def is_allowed(self, *, user: UserContext | None) -> bool:
        """Проверяет, разрешено ли действие для пользователя."""
