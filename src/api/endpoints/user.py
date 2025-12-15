from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.permissions import allow_anonymous_or_roles
from api.exceptions import UserAlreadyExistsHTTP
from core.db import get_async_session
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
    actor: User | None = Depends(
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


# @router.get(
#     '/',
#     response_model=list[UserDB],
#     status_code=status.HTTP_200_OK,
#     summary='Получение списка пользователей',
# )
# async def get_all_users(
#     session: AsyncSession = Depends(get_async_session),
# )->list[UserDB]:
#     pass
