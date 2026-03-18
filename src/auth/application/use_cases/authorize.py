from auth.application.use_cases.exceptions import AccessDenied, InactiveAccount
from auth.domain.permissions.base import PermissionPolicy
from auth.domain.permissions.context import UserContext


class AuthorizationUseCase:
    """Класс для авторизации пользователей."""

    def __init__(self, policy: PermissionPolicy) -> None:
        """Инициализирует класс для авторизации пользователей."""
        self.policy = policy

    def execute(
        self,
        *,
        user: UserContext | None,
    ) -> None:
        """Выполняет авторизацию пользователя."""
        if user is not None and not user.is_active:
            raise InactiveAccount()

        if not self.policy.is_allowed(user=user):
            raise AccessDenied()
