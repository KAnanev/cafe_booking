from typing import Any, Callable, Coroutine

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from api.exceptions import (
    UserNotFoundHTTP,
)
from core.db import get_async_session
from core.logging import set_user_context
from core.security import decode_access_token
from crud.user import user_crud
from managers.exceptions import PermissionDenied, UserInactive
from models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl='/auth/login',
    auto_error=False,
)


async def get_current_user(
    session: AsyncSession = Depends(get_async_session),
    token: str = Depends(oauth2_scheme),
) -> User:
    """Возвращает текущего аутентифицированного пользователя.

    Использовать, когда:
    - нужна только проверка JWT и загрузка пользователя из БД
    - логирование пользователя не требуется
    - dependency используется во внутренних сервисах, фоновых задачах
    или тестах
    - требуется минимальная зависимость без побочных эффектов

    Выполняет:
    - извлечение access-токена из заголовка Authorization
    - декодирование JWT
    - загрузку пользователя из базы данных
    - проверку активности пользователя (is_active)

    Не выполняет:
    - установку контекста логирования
    - проверку ролей
    """
    user_id = decode_access_token(token)

    user = await user_crud.get_by_id(obj_id=user_id, session=session)
    if not user:
        raise UserNotFoundHTTP()

    if not user.is_active:
        raise UserInactive('Пользователь неактивен')
    return user


async def get_current_active_user(
    user: User = Depends(get_current_user),
) -> User:
    """Возвращает текущего пользователя с установленным контекстом логирования.

    Использовать, когда:
    - dependency применяется в HTTP-эндпоинтах FastAPI
    - требуется логирование с привязкой к пользователю
    - необходимо единообразное заполнение user-context для логов и трассировки

    Выполняет:
    - установку контекста пользователя для логирования (user_id, email, role)
    - возвращает уже аутентифицированного и активного пользователя

    Рекомендуется использовать:
    - напрямую в эндпоинтах
    - как базовую зависимость для require_role(...)
    """
    set_user_context(
        user_id=user.id,
        username=user.email,
        email=user.email,
        role=user.role.name if hasattr(user.role, 'name') else str(user.role),
    )
    return user


def require_role(
    *allowed_roles: UserRole,
) -> Callable[..., Coroutine[Any, Any, User]]:
    """Dependency-фабрика для проверки роли пользователя.

    Использовать, когда:
    - требуется ограничить доступ к эндпоинту по ролям
    - необходимо логирование пользователя (через get_current_active_user)
    - эндпоинт доступен только ADMIN / MANAGER / и т.д.

    Особенности:
    - автоматически включает аутентификацию
    - автоматически устанавливает контекст логирования
    - проверяет, что роль пользователя входит в allowed_roles

    Пример:
        Depends(require_role(UserRoles.ADMIN, UserRoles.MANAGER))
    """

    async def role_checker(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        """Проверяет роль текущего пользователя."""
        if current_user.role not in allowed_roles:
            raise PermissionDenied()
        return current_user

    return role_checker
