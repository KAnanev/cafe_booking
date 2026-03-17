import uuid

from auth.domain.permissions.context import UserContext, UserRole
from auth.domain.permissions.presets import (
    optional_user,
    require_admin,
    require_admin_or_manager,
    require_anonymous_or_admin_or_manager,
    require_auth,
)
from auth.use_cases.authorize import AuthorizationUseCase


class FakeUser(UserContext):
    """Класс-обертка для контекста пользователя."""

    pass


class TestAuthorizeUseCase:
    """Класс для тестирования случаев авторизации."""

    def test_inactive_user_disallow(self) -> None:
        """Доступ запрещен для неактивного пользователя.

        При использовании различных предустановленных правил
        аутентификации и авторизации.
        """
        presets = [
            require_auth,
            require_admin,
            require_admin_or_manager,
            require_anonymous_or_admin_or_manager,
            optional_user,
        ]

        inactive_user = FakeUser(uuid.uuid4(), UserRole.USER, is_active=False)

        for preset in presets:
            auth_case = AuthorizationUseCase(preset)
            assert auth_case.execute(user=inactive_user) is None
