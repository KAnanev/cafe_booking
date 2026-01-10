from typing import Optional

from pydantic import EmailStr
from sqlalchemy import exists, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase
from models.user import User
from schemas.user import UserAdminUpdate, UserCreateDB


class UserCRUD(CRUDBase[User, UserCreateDB, UserAdminUpdate]):
    """CRUD-методы для User, включая специализированные запросы."""

    async def get_by_email(
        self,
        session: AsyncSession,
        *,
        email: str,
    ) -> Optional[User]:
        """Возвращает пользователя по email."""
        stmt = select(self._model).where(self._model.email == email)
        result = await session.execute(stmt)
        return result.scalars().first()

    async def exists_by_email(
        self,
        session: AsyncSession,
        *,
        email: EmailStr,
    ) -> bool:
        """Проверяет существование пользователя с указанным email."""
        stmt = select(exists().where(self._model.email == email))
        return bool(await session.scalar(stmt))

    async def exists_by_phone(
        self,
        session: AsyncSession,
        *,
        phone: str,
    ) -> bool:
        """Проверяет существование пользователя с указанным телефоном."""
        stmt = select(exists().where(self._model.phone == phone))
        return bool(await session.scalar(stmt))

    async def get_by_login(
        self,
        session: AsyncSession,
        *,
        login: str,
    ) -> Optional[User]:
        """Получает пользователя по email или телефону."""
        stmt = select(self._model).where(
            or_(self._model.email == login, self._model.phone == login),
        )
        result = await session.execute(stmt)
        return result.scalars().first()


user_crud: UserCRUD = UserCRUD(User)
