from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase
from models.user import User
from schemas.user import UserCreate, UserUpdate


class UserCRUD(CRUDBase[User, UserCreate, UserUpdate]):
    """CRUD операции для User."""

    async def get_by_email_or_phone(
        self,
        user: UserCreate,
        session: AsyncSession,
    ) -> User | None:
        """Получает пользователя по email или телефону."""
        stmt = select(User).where(
            or_(User.email == user.email, User.phone == user.phone),
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()


user_crud = UserCRUD(User)
