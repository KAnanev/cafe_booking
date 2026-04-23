from typing import Callable

from fastapi import Depends

from accounts.auth import PermissionPolicy, UserContext
from accounts.auth.application import AuthorizationUseCase
from api.dependencies.auth import get_optional_user


def require_permission(
    policy: PermissionPolicy,
) -> Callable:
    """Требует наличия прав для выполнения действия."""

    def dependency(
        user: UserContext | None = Depends(get_optional_user),
    ) -> UserContext | None:
        """Проверяет права пользователя на выполнение действия."""
        AuthorizationUseCase(policy=policy).execute(
            user=user,
        )
        return user

    return dependency
