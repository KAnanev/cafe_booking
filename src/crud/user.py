from typing import Optional

from sqlalchemy import exists, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase
from models.user import User
from schemas.user import UserAdminUpdate, UserCreate


class UserCRUD(CRUDBase[User, UserCreate, UserAdminUpdate]):
    """CRUD операции для модели User."""

    async def get_by_email(
        self,
        *,
        email: str,
        session: AsyncSession,
    ) -> Optional[User]:
        """Возвращает пользователя по email."""
        stmt = select(User).where(User.email == email)
        result = await session.execute(stmt)
        return result.scalars().first()

    async def exists_by_email(
        self,
        email: str,
        session: AsyncSession,
    ) -> bool:
        """Проверяет существование пользователя с указанным email."""
        stmt = select(exists().where(User.email == email))
        return await session.scalar(stmt)

    async def exists_by_phone(
        self,
        phone: str,
        session: AsyncSession,
    ) -> bool:
        """Проверяет существование пользователя с указанным телефоном."""
        stmt = select(exists().where(User.phone == phone))
        return await session.scalar(stmt)

    async def get_by_login(
        self,
        login: str,
        session: AsyncSession,
    ) -> Optional[User]:
        """Получает пользователя по email или номеру телефона."""
        stmt = select(User).where(
            or_(
                User.email == login,
                User.phone == login,
            ),
        )

        result = await session.execute(stmt)
        return result.scalars().first()


user_crud = UserCRUD(User)
