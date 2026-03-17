from .base import PermissionPolicy
from .context import UserContext


class AllOf(PermissionPolicy):
    """Проверяет, удовлетворяют ли все политики доступа."""

    def __init__(self, *policies: PermissionPolicy) -> None:
        """Проверяет, удовлетворяют ли все политики доступа."""
        self._policies = policies

    def is_allowed(
        self,
        *,
        user: UserContext | None,
        action: str,
    ) -> bool:
        """Проверяет, удовлетворяют ли все политики доступа."""
        return all(
            policy.is_allowed(user=user, action=action)
            for policy in self._policies
        )


class AnyOf(PermissionPolicy):
    """Проверяет, удовлетворяют ли хотя бы одна политика доступа."""

    def __init__(self, *policies: PermissionPolicy) -> None:
        """Проверяет, удовлетворяют ли хотя бы одна политика доступа."""
        self._policies = policies

    def is_allowed(
        self,
        *,
        user: UserContext | None,
        action: str,
    ) -> bool:
        """Проверяет, удовлетворяют ли хотя бы одна политика доступа."""
        return any(
            policy.is_allowed(user=user, action=action)
            for policy in self._policies
        )
