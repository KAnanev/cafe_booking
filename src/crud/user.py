from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase
from models.user import User
from schemas.user import UserCreate, UserUpdate


class UserCRUD(CRUDBase[User, UserCreate, UserUpdate]):
    """CRUD операции для модели User."""

    async def get_by_email(
        self,
        email: str,
        session: AsyncSession,
    ) -> Optional[User]:
        """Получает пользователя по адресу электронной почты."""
        result = await session.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def get_by_phone(
        self,
        phone: str,
        session: AsyncSession,
    ) -> Optional[User]:
        """Получает пользователя по номеру телефона."""
        result = await session.execute(select(User).where(User.phone == phone))
        return result.scalars().first()


user_crud = UserCRUD(User)
