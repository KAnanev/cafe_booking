from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from crud.cafe import cafe_crud
from crud.table import table_crud
from managers.exceptions import PermissionDenied, TableNotFound
from models.table import Table
from models.user import User, UserRole
from schemas.table import TableCreate, TableUpdate


class TableManager:
    """Менеджер столов: бизнес-логика и оркестрация операций со столами."""

    def __init__(self, session: AsyncSession) -> None:
        """Сохранить сессию БД для выполнения операций."""
        self._session = session

    async def _get_manager_cafe_ids(self, manager_id: UUID) -> list[UUID]:
        cafes = await cafe_crud.get_managed_cafes(
            session=self._session,
            user_id=manager_id,
        )
        return [cafe.id for cafe in cafes]

    async def _ensure_can_manage_cafe(self, cafe_id: UUID, user: User) -> None:
        if user.role == UserRole.ADMIN:
            return
        if user.role == UserRole.MANAGER:
            cafe_ids = await self._get_manager_cafe_ids(user.id)
            if cafe_id in cafe_ids:
                return
        raise PermissionDenied('Нет доступа.')

    async def list_tables(self, cafe_id: UUID, show_all: bool) -> list[Table]:
        """Вернуть список столов указанного кафе."""
        return await table_crud.get_by_cafe(
            session=self._session,
            cafe_id=cafe_id,
            show_all=show_all,
        )

    async def get_table(self, cafe_id: UUID, table_id: UUID) -> Table:
        """Вернуть стол по id в рамках кафе или выбросить TableNotFound."""
        table = await table_crud.get_by_cafe_and_id(
            session=self._session,
            cafe_id=cafe_id,
            table_id=table_id,
            show_all=True,
        )
        if table is None:
            raise TableNotFound('Стол не найден')
        return table

    async def create_table(
        self,
        cafe_id: UUID,
        table_in: TableCreate,
        current_user: User,
    ) -> Table:
        """Создать стол в кафе. cafe_id берётся из пути."""
        await self._ensure_can_manage_cafe(cafe_id=cafe_id, user=current_user)

        table_in = table_in.model_copy(update={'cafe_id': cafe_id})
        return await table_crud.create(
            obj_in=table_in,
            session=self._session,
        )

    async def update_table(
        self,
        cafe_id: UUID,
        table_id: UUID,
        table_in: TableUpdate,
        current_user: User,
    ) -> Table:
        """Обновить стол в рамках кафе. Изменение cafe_id запрещено."""
        await self._ensure_can_manage_cafe(cafe_id=cafe_id, user=current_user)

        table = await self.get_table(cafe_id=cafe_id, table_id=table_id)
        update_data = table_in.model_dump(
            exclude_unset=True,
            exclude={'cafe_id'},
        )
        return await table_crud.update(
            db_obj=table,
            obj_in=update_data,
            session=self._session,
        )
