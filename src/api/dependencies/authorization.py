from typing import Callable

from fastapi import Depends

from api.dependencies.auth import get_optional_user
from auth.application.use_cases.authorize import AuthorizationUseCase
from auth.domain.permissions.base import PermissionPolicy
from auth.domain.permissions.context import UserContext


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
