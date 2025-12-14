from sqlalchemy.ext.asyncio import AsyncSession

from core.security import get_password_hash
from crud.user import user_crud
from models.user import User, UserRole
from schemas.user import UserCreate, UserCreateDB


class UserManager:
    """Менеджер пользователей."""

    def __init__(self, session: AsyncSession) -> None:
        """Инициализирует менеджер сессией базы данных."""
        self.session = session

    async def _create_user(
        self,
        user: UserCreate,
        role: UserRole = UserRole.USER,
        is_superuser: bool = False,
    ) -> User:
        """Приватный метод для создания пользователя.

        Проверяются поля email и телефона.
        """
        if user.email is not None:
            existing_by_email = await user_crud.get_by_email(
                user.email,
                session=self.session,
            )
            if existing_by_email:
                raise ValueError(f'Пользователь {user.email} уже существует')

        if user.phone is not None:
            existing_by_phone = await user_crud.get_by_phone(
                user.phone,
                session=self.session,
            )
            if existing_by_phone:
                raise ValueError(f'Пользователь {user.phone} уже существует')

        hashed_password = get_password_hash(user.password)
        user_internal = UserCreateDB(
            **user.model_dump(exclude={'password'}),
            hashed_password=hashed_password,
            role=role,
            is_superuser=is_superuser,
        )

        return await user_crud.create(
            obj_in=user_internal,
            session=self.session,
        )

    async def create_user(self, user: UserCreate) -> User:
        """Создаёт обычного пользователя (роль USER)."""
        return await self._create_user(user=user)

    async def create_manager(
        self,
        user: UserCreate,
    ) -> User:
        """Создаёт пользователя с ролью MANAGER."""
        return await self._create_user(user=user, role=UserRole.MANAGER)

    async def create_admin(
        self,
        user: UserCreate,
    ) -> User:
        """Создаёт пользователя с ролью ADMIN."""
        return await self._create_user(user=user, role=UserRole.ADMIN)

    async def create_superuser(self, user: UserCreate) -> User:
        """Создаёт суперпользователя (роль ADMIN + is_superuser=True)."""
        return await self._create_user(
            user=user,
            role=UserRole.ADMIN,
            is_superuser=True,
        )
