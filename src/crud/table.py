import uuid
from typing import Optional

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase
from models import Cafe
from models.cafe import CafeManagerLink
from models.table import Table
from schemas.table import TableCreate, TableUpdate


class TableCRUD(CRUDBase[Table, TableCreate, TableUpdate]):
    """CRUD для столов."""

    def _query_for_admin(self, *, cafe_id: uuid.UUID) -> Select:
        """Готовит запрос для админов."""
        return (
            self._select_base()
            .join(Cafe, Cafe.id == self._model.cafe_id)
            .where(self._model.cafe_id == cafe_id)
        )

    def _query_for_user(self, *, cafe_id: uuid.UUID) -> Select:
        """Готовит запрос для пользователей."""
        return (
            self._select_base()
            .join(Cafe, Cafe.id == self._model.cafe_id)
            .where(self._model.cafe_id == cafe_id)
            .where(Cafe.is_active.is_(True))
        )

    def _query_for_manager(
        self,
        *,
        cafe_id: uuid.UUID,
        manager_id: uuid.UUID,
    ) -> Select:
        """Готовит запрос для менеджеров."""
        return (
            self._select_base()
            .join(Cafe, Cafe.id == self._model.cafe_id)
            .join(CafeManagerLink, CafeManagerLink.cafe_id == Cafe.id)
            .where(self._model.cafe_id == cafe_id)
            .where(CafeManagerLink.user_id == manager_id)
            .where(CafeManagerLink.is_active.is_(True))
        ).distinct()

    async def list_for_user(
        self,
        session: AsyncSession,
        *,
        cafe_id: uuid.UUID,
    ) -> list[Table]:
        """Возвращает список объектов для пользователей."""
        query = self._query_for_user(cafe_id=cafe_id)
        return await self.list(session, only_active=True, query=query)

    async def get_for_user(
        self,
        session: AsyncSession,
        *,
        cafe_id: uuid.UUID,
        table_id: uuid.UUID,
    ) -> Optional[Table]:
        """Возвращает объект для пользователя."""
        query = self._query_for_user(cafe_id=cafe_id).where(
            self._model.id == table_id,
        )
        return await self.get(
            session,
            obj_id=table_id,
            only_active=True,
            query=query,
        )

    async def list_for_manager(
        self,
        session: AsyncSession,
        *,
        cafe_id: uuid.UUID,
        manager_id: uuid.UUID,
        only_active: bool,
    ) -> list[Table]:
        """Возвращает список объектов для менеджеров."""
        query = self._query_for_manager(cafe_id=cafe_id, manager_id=manager_id)
        return await self.list(session, only_active=only_active, query=query)

    async def get_for_manager(
        self,
        session: AsyncSession,
        *,
        cafe_id: uuid.UUID,
        table_id: uuid.UUID,
        manager_id: uuid.UUID,
        only_active: bool,
    ) -> Optional[Table]:
        """Возвращает объект для менеджеров."""
        query = self._query_for_manager(
            cafe_id=cafe_id,
            manager_id=manager_id,
        ).where(self._model.id == table_id)
        return await self.get(
            session,
            obj_id=table_id,
            only_active=only_active,
            query=query,
        )

    async def list_for_admin(
        self,
        session: AsyncSession,
        *,
        cafe_id: uuid.UUID,
        only_active: bool,
    ) -> list[Table]:
        """Возвращает список объектов для админов."""
        query = self._query_for_admin(cafe_id=cafe_id)
        return await self.list(session, only_active=only_active, query=query)

    async def get_for_admin(
        self,
        session: AsyncSession,
        *,
        cafe_id: uuid.UUID,
        table_id: uuid.UUID,
        only_active: bool,
    ) -> Optional[Table]:
        """Возвращает объект для админов."""
        query = self._query_for_admin(cafe_id=cafe_id).where(
            self._model.id == table_id,
        )
        return await self.get(
            session,
            obj_id=table_id,
            only_active=only_active,
            query=query,
        )


table_crud: TableCRUD = TableCRUD(Table)
