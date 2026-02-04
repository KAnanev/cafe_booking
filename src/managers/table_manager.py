from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from auth.domain.permissions.context import UserRole
from crud.table import table_crud
from managers.cafe_access import CafePermissionService
from managers.exceptions import CafeNotFound, TableNotFound
from models import Cafe
from models.table import Table
from models.user import User
from schemas.table import TableCreate, TableUpdate


class TableManager:
    """Менеджер столов: бизнес-логика и оркестрация операций со столами."""

    def __init__(
        self,
        session: AsyncSession,
        cafe_permissions: CafePermissionService,
    ) -> None:
        """Сохранить сессию БД для выполнения операций."""
        self._table_crud = table_crud
        self._session = session
        self._cafe_permissions = cafe_permissions

    async def list(
        self,
        *,
        user: User,
        cafe_id: uuid.UUID,
        show_all: bool = False,
    ) -> list[Table]:
        """Возвращает список столов."""
        if user.role == UserRole.USER:
            return await self._table_crud.list_for_user(
                self._session,
                cafe_id=cafe_id,
            )

        only_active = not show_all

        if user.role == UserRole.MANAGER:
            return await self._table_crud.list_for_manager(
                self._session,
                cafe_id=cafe_id,
                manager_id=user.id,
                only_active=only_active,
            )

        return await self._table_crud.list_for_admin(
            self._session,
            cafe_id=cafe_id,
            only_active=only_active,
        )

    async def get(
        self,
        *,
        user: User,
        cafe_id: uuid.UUID,
        table_id: uuid.UUID,
    ) -> Table:
        """Возвращает стол."""
        if user.role == UserRole.USER:
            table = await self._table_crud.get_for_user(
                self._session,
                cafe_id=cafe_id,
                table_id=table_id,
            )
        elif user.role == UserRole.MANAGER:
            table = await self._table_crud.get_for_manager(
                self._session,
                cafe_id=cafe_id,
                table_id=table_id,
                manager_id=user.id,
                only_active=False,
            )
        else:
            table = await self._table_crud.get_for_admin(
                self._session,
                cafe_id=cafe_id,
                table_id=table_id,
                only_active=False,
            )

        if table is None:
            raise TableNotFound('Стол не найден')
        return table

    async def create(
        self,
        *,
        user: User,
        cafe_id: uuid.UUID,
        obj_in: TableCreate,
    ) -> Table:
        """Создает стол."""
        cafe_exists = await self._table_crud.exists_by_id(
            self._session,
            model=Cafe,
            obj_id=cafe_id,
        )

        if not cafe_exists:
            raise CafeNotFound('Кафе не найдено')

        await self._cafe_permissions.check_manager_of_cafe(
            cafe_id=cafe_id,
            user=user,
        )

        return await self._table_crud.create_for_parent(
            self._session,
            parent_field='cafe_id',
            parent_id=cafe_id,
            user_id=user.id,
            obj_in=obj_in,
        )

    async def update(
        self,
        *,
        user: User,
        cafe_id: uuid.UUID,
        table_id: uuid.UUID,
        obj_in: TableUpdate,
    ) -> Table:
        """Обновляет стол."""
        table = await self.get(user=user, cafe_id=cafe_id, table_id=table_id)

        if table is None:
            raise TableNotFound('Стол не найден')

        await self._cafe_permissions.check_manager_of_cafe(
            cafe_id=cafe_id,
            user=user,
        )

        return await self._table_crud.update(
            self._session,
            db_obj=table,
            obj_in=obj_in,
        )
