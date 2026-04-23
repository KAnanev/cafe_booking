from accounts.auth import PermissionPolicy, UserContext, UserRole


class IsAuthenticated(PermissionPolicy):
    """Проверяет, аутентифицирован ли пользователь."""

    def is_allowed(self, *, user: UserContext | None) -> bool:
        """Проверяет, аутентифицирован ли пользователь."""
        return user is not None


class IsActiveUser(PermissionPolicy):
    """Проверяет, активный ли пользователь."""

    def is_allowed(self, *, user: UserContext | None) -> bool:
        """Проверяет, активный ли пользователь."""
        return user is not None and user.is_active


class HasRole(PermissionPolicy):
    """Проверяет, имеет ли пользователь указанные роли."""

    def __init__(self, *allowed_roles: UserRole) -> None:
        """Инициализирует политику проверки ролей."""
        self._allowed_roles = set(allowed_roles)

    def is_allowed(self, *, user: UserContext | None) -> bool:
        """Проверяет, имеет ли пользователь указанные роли."""
        return user is not None and user.role in self._allowed_roles


class IsAnonymous(PermissionPolicy):
    """Проверяет, анонимный ли пользователь."""

    def is_allowed(self, *, user: UserContext | None) -> bool:
        """Проверяет, анонимный ли пользователь."""
        return user is None
