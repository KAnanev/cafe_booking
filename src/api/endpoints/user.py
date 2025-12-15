from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.exceptions import UserAlreadyExistsHTTP
from core.db import get_async_session
from managers.exceptions import UserAlreadyExists
from managers.user_manager import UserManager
from schemas.user import UserCreate, UserDB

router = APIRouter()


@router.post(
    '/',
    response_model=UserDB,
    status_code=status.HTTP_201_CREATED,
    summary='Регистрация нового пользователя.',
)
async def create_user(
    user: UserCreate,
    session: AsyncSession = Depends(get_async_session),
) -> UserDB:
    """Создает нового пользователя с указанными данными.

    **Обязательные поля:**

    - username
    - password
    - email или phone
    """
    manager = UserManager(session=session)
    try:
        user = await manager.create_user(user=user)
        return UserDB.model_validate(user, from_attributes=True)
    except UserAlreadyExists as exc:
        raise UserAlreadyExistsHTTP(str(exc))
