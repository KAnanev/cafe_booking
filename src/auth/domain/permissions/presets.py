from .atomic import (
    HasRole,
    IsActiveUser,
    IsAnonymous,
    IsAuthenticated,
)
from .composite import AllOf, AnyOf
from .context import UserRole

require_auth = AllOf(
    IsAuthenticated(),
    IsActiveUser(),
    HasRole(UserRole.ADMIN, UserRole.MANAGER, UserRole.USER),
)

require_admin = AllOf(
    IsAuthenticated(),
    IsActiveUser(),
    HasRole(UserRole.ADMIN),
)

require_admin_or_manager = AllOf(
    IsAuthenticated(),
    IsActiveUser(),
    HasRole(UserRole.ADMIN, UserRole.MANAGER),
)

require_anonymous_or_admin_or_manager = AnyOf(
    IsAnonymous(),
    require_admin_or_manager,
)

optional_user = AnyOf(
    IsAnonymous(),
    HasRole(UserRole.ADMIN, UserRole.MANAGER, UserRole.USER),
)
