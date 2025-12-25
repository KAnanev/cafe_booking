from uuid import UUID

from fastapi import APIRouter, Depends, status

from api.dependencies.auth import (
    require_admin_or_manager,
    require_anonymous_or_admin_or_manager,
    require_auth,
)
from api.dependencies.managers import get_user_manager
from managers.user_manager import UserManager
from models.user import User
from schemas.user import UserAdminUpdate, UserCreate, UserDB, UserMeUpdate

router = APIRouter()


@router.post(
    '/',
    response_model=UserDB,
    status_code=status.HTTP_201_CREATED,
    summary='Регистрация нового пользователя.',
)
async def create_user(
    user_in: UserCreate,
    _: User | None = require_anonymous_or_admin_or_manager,
    user_manager: UserManager = Depends(get_user_manager),
) -> UserDB:
    """Создает нового пользователя с указанными данными.

    **Обязательные поля:**

    - username
    - password
    - email или phone
    """
    user = await user_manager.create_user(user=user_in)
    return UserDB.model_validate(user)


@router.get(
    '/',
    response_model=list[UserDB],
    status_code=status.HTTP_200_OK,
    summary='Получение списка пользователей',
)
async def get_all_users(
    _: User = require_admin_or_manager,
    user_manager: UserManager = Depends(get_user_manager),
) -> list[UserDB]:
    """Возвращает информацию о всех пользователях.

    Только для администраторов или менеджеров.
    """
    users = await user_manager.get_multi()
    return [UserDB.model_validate(user) for user in users]


@router.get(
    '/me',
    response_model=UserDB,
    status_code=status.HTTP_200_OK,
    summary='Получение информации о текущем пользователе',
)
async def get_me(
    user: User = require_auth,
) -> UserDB:
    """Возвращает информацию о текущем пользователе.

    Только для авторизированных пользователей.
    """
    return UserDB.model_validate(user)


@router.patch(
    '/me',
    response_model=UserDB,
    status_code=status.HTTP_200_OK,
    summary='Обновление информации о текущем пользователе',
)
async def update_me(
    data: UserMeUpdate,
    user: User = require_auth,
    user_manager: UserManager = Depends(get_user_manager),
) -> UserDB:
    """Возвращает обновленную информацию о пользователе.

    Только для авторизированных пользователей.
    """
    updated = await user_manager.update_user(
        actor=user,
        target=user,
        data=data,
    )
    return UserDB.model_validate(updated)


@router.get(
    '/{user_id}',
    response_model=UserDB,
    status_code=status.HTTP_200_OK,
    summary='Получение информации о пользователе по его ID',
)
async def get_user(
    user_id: UUID,
    _: User = require_admin_or_manager,
    user_manager: UserManager = Depends(get_user_manager),
) -> UserDB:
    """Возвращает информацию о пользователе по его ID.

    Только для администраторов или менеджеров.
    """
    user = await user_manager.get_by_id(user_id)
    return UserDB.model_validate(user)


@router.patch(
    '/{user_id}',
    response_model=UserDB,
    status_code=status.HTTP_200_OK,
    summary='Обновление информации о пользователе по его ID',
)
async def update_user(
    user_id: UUID,
    data: UserAdminUpdate,
    actor: User = require_admin_or_manager,
    user_manager: UserManager = Depends(get_user_manager),
) -> UserDB:
    """Возвращает обновленную информацию о пользователе по его ID.

    Только для администраторов или менеджеров.
    """
    target = await user_manager.get_by_id(user_id)
    updated = await user_manager.update_user(
        actor=actor,
        target=target,
        data=data,
    )
    return UserDB.model_validate(updated)
