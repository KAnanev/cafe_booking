from typing import Any, Coroutine, Sequence

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Row, RowMapping

from core.db import get_async_session
from core.base import User

from core.user import auth_backend, fastapi_users
from schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter()

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix='/auth',
    tags=['auth'],
)

# router.include_router(
#     fastapi_users.get_register_router(UserRead, UserCreate),
#     prefix='/auth',
#     tags=['auth'],
# )

users_router = fastapi_users.get_users_router(UserCreate, UserRead, UserUpdate)

users_router.routes = [
    rout for rout in users_router.routes if rout.name != 'users:delete_user'
]

router.include_router(
    users_router,
    prefix='/users',
    tags=['users'],
)

@router.get('/users', response_model=list[UserRead])
async def get_all_users(
        skip=0, limit=100, session: AsyncSession = Depends(get_async_session)
) -> Sequence[User]:
    """Получить список всех пользователей."""
    result = await session.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()
