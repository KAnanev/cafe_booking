from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.permissions import allow_anonymous_or_roles
from api.dependencies.users import require_role
from api.exceptions import UserAlreadyExistsHTTP, UserNotFoundHTTP
from core.db import get_async_session
from crud.user import user_crud
from managers.exceptions import UserAlreadyExists
from managers.user_manager import UserManager
from models.user import User, UserRoles
from schemas.user import UserCreate, UserDB

router = APIRouter()


@router.post(
    '/',
    response_model=UserDB,
    status_code=status.HTTP_201_CREATED,
    summary='Регистрация нового пользователя.',
)
async def create_user(
    user_in: UserCreate,
    session: AsyncSession = Depends(get_async_session),
    _: User | None = Depends(
        allow_anonymous_or_roles(
            UserRoles.ADMIN,
            UserRoles.MANAGER,
        ),
    ),
) -> UserDB:
    """Создает нового пользователя с указанными данными.

    **Обязательные поля:**

    - username
    - password
    - email или phone
    """
    manager = UserManager(session=session)
    try:
        user_in = await manager.create_user(user=user_in)
        return UserDB.model_validate(user_in, from_attributes=True)
    except UserAlreadyExists as exc:
        raise UserAlreadyExistsHTTP(str(exc))


@router.get(
    '/',
    response_model=list[UserDB],
    status_code=status.HTTP_200_OK,
    summary='Получение списка пользователей',
)
async def get_all_users(
    session: AsyncSession = Depends(get_async_session),
    _: User = Depends(require_role(UserRoles.ADMIN, UserRoles.MANAGER)),
) -> list[UserDB]:
    """Возвращает информацию о всех пользователях.

    Только для администраторов или менеджеров.
    """
    return await user_crud.get_multi(session=session)


@router.get(
    '/{user_id}',
    response_model=UserDB,
    status_code=status.HTTP_200_OK,
    summary='Получение информации о пользователе по его ID',
)
async def get_user(
    user_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    _: User = Depends(require_role(UserRoles.ADMIN, UserRoles.MANAGER)),
) -> UserDB:
    """Возвращает информацию о пользователе по его ID.

    Только для администраторов или менеджеров
    """
    user = await user_crud.get_by_id(session=session, obj_id=user_id)

    if not user:
        raise UserNotFoundHTTP()

    return UserDB.model_validate(user, from_attributes=True)
