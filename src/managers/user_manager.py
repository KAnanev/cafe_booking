from typing import Union

from sqlalchemy.ext.asyncio import AsyncSession

from core.constants import ADMIN_ONLY_USER_UPDATE_FIELDS
from core.security import get_password_hash
from crud.user import user_crud
from managers.exceptions import PermissionDenied, UserAlreadyExists
from models.user import User, UserRole
from schemas.user import (
    UserAdminUpdate,
    UserCreate,
    UserCreateDB,
    UserMeUpdate,
)


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
        await self._check_unique_fields(user)

        hashed_password = get_password_hash(user.password)
        user_internal = UserCreateDB(
            **user.model_dump(exclude={'password', 'role'}),
            hashed_password=hashed_password,
            role=role,
            is_superuser=is_superuser,
        )

        return await user_crud.create(
            obj_in=user_internal,
            session=self.session,
        )

    async def _check_unique_fields(self, user: UserCreate) -> None:
        """Проверяет уникальность email и телефона пользователя."""
        if user.email:
            if await user_crud.get_by_email(user.email, session=self.session):
                raise UserAlreadyExists(
                    f"Пользователь с email '{user.email}' уже существует",
                )

        if user.phone:
            if await user_crud.get_by_phone(user.phone, session=self.session):
                raise UserAlreadyExists(
                    f"Пользователь с телефоном '{user.phone}' уже существует",
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

    async def update_user(
        self,
        actor: User,
        target: User,
        data: Union[UserMeUpdate, UserAdminUpdate],
    ) -> User:
        """Обновляет поля пользователя."""
        self._check_update_permissions(actor, target, data)

        return await user_crud.update(
            db_obj=target,
            obj_in=data,
            session=self.session,
        )

    def _check_update_permissions(
        self,
        actor: User,
        target: User,
        data: Union[UserMeUpdate, UserAdminUpdate],
    ) -> None:
        """Проверяет права на изменение полй."""
        if actor.role == UserRole.USER and actor.id != target.id:
            raise PermissionDenied('Нельзя изменять других пользователей')

        admin_only_fields = ADMIN_ONLY_USER_UPDATE_FIELDS

        for field in admin_only_fields:
            if getattr(data, field, None) is not None:
                if actor.role != UserRole.ADMIN:
                    raise PermissionDenied(
                        f"Поле '{field}' доступно только администратору",
                    )
