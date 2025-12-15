from http import HTTPStatus
from typing import Callable, Optional
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.users import get_current_user, oauth2_scheme
from api.exceptions import PermissionDeniedHTTP
from core.db import get_async_session
from core.exceptions import InvalidToken
from core.security import decode_access_token
from crud.cafe import cafe_crud
from crud.user import user_crud
from models.user import User, UserRoles


def allow_anonymous_or_roles(
    *allowed_roles: UserRoles,
) -> Callable[[User], User]:
    """Фабрика зависимостей доступа для эндпоинтов FastAPI.

    Разрешает выполнение эндпоинта в двух случаях:
    1. Запрос выполнен неавторизованным пользователем (отсутствует JWT-токен).
    2. Запрос выполнен авторизованным пользователем, роль которого
    входит в список `allowed_roles`.

    Используется в сценариях, где операция доступна:
    - для анонимных пользователей (например, регистрация);
    - для административных ролей (ADMIN, MANAGER);
    - но запрещена для обычных авторизованных пользователей (USER).
    """

    async def dependency(
        token: str | None = Depends(oauth2_scheme),
        session: AsyncSession = Depends(get_async_session),
    ) -> Optional[User]:
        """Проверяет право доступа текущего пользователя к эндпоинту.

        Логика:
        - если JWT-токен отсутствует — пользователь считается анонимным,
          доступ разрешается;
        - если токен присутствует, но невалиден — пользователь считается
          анонимным;
        - если пользователь найден и активен — проверяется его роль;
        - если роль не входит в список разрешённых — доступ запрещается.
        """
        if not token:
            return None

        try:
            user_id = decode_access_token(token)
        except InvalidToken:
            return None

        user = await user_crud.get_by_id(user_id, session)

        if not user or not user.is_active:
            raise PermissionDeniedHTTP()

        if user.role not in allowed_roles:
            raise PermissionDeniedHTTP(
                'Авторизованным пользователям без прав доступ запрещен.',
            )

        return user

    return dependency


async def is_manager_or_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Разрешает доступ только менеджерам и админам."""
    if current_user.role in (UserRoles.MANAGER, UserRoles.ADMIN):
        return current_user
    raise HTTPException(
        status_code=HTTPStatus.FORBIDDEN,
        detail='Недостаточно прав.',
    )


async def can_manage_cafe(
    cafe_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> User:
    """Проверка права управления конкретным кафе."""
    if current_user.role == UserRoles.ADMIN:
        return current_user

    if current_user.role != UserRoles.MANAGER:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Недостаточно прав для управления этим кафе.',
        )

    managed_cafes = await cafe_crud.get_managed_cafes(
        session=session,
        user_id=current_user.id,
    )
    if any(cafe.id == cafe_id for cafe in managed_cafes):
        return current_user

    raise HTTPException(
        status_code=HTTPStatus.FORBIDDEN,
        detail='Пользователь не является менеджером этого кафе.',
    )
