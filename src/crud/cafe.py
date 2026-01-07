import uuid
from typing import Optional

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase
from models.cafe import Cafe, CafeManagerLink
from schemas.cafe import CafeCreate, CafeUpdate


class CafeCRUD(CRUDBase[Cafe, CafeCreate, CafeUpdate]):
    """CRUD для кафе."""

    def _query_for_manager(
        self,
        *,
        manager_id: uuid.UUID,
        only_active: bool = True,
    ) -> Select:
        """Строит запрос на выборку кафе, доступных конкретному менеджеру."""
        query = (
            self._select_base()
            .join(CafeManagerLink, CafeManagerLink.cafe_id == self._model.id)
            .where(CafeManagerLink.user_id == manager_id)
            .where(CafeManagerLink.is_active.is_(True))
        )

        if only_active and hasattr(self._model, 'is_active'):
            query = query.where(self._model.is_active.is_(True))  # type: ignore[attr-defined]

        return query.distinct()

    async def list_for_manager(
        self,
        session: AsyncSession,
        *,
        manager_id: uuid.UUID,
        only_active: bool = True,
    ) -> list[Cafe]:
        """Возвращает список кафе, которыми управляет менеджер."""
        query = self._query_for_manager(
            manager_id=manager_id,
            only_active=only_active,
        )
        result = await session.execute(query)
        return list(result.scalars().all())

    async def get_for_manager(
        self,
        session: AsyncSession,
        *,
        obj_id: uuid.UUID,
        manager_id: uuid.UUID,
        only_active: bool = True,
    ) -> Optional[Cafe]:
        """Возвращает кафе по id, если оно доступно менеджеру."""
        query = self._query_for_manager(
            manager_id=manager_id,
            only_active=only_active,
        ).where(self._model.id == obj_id)
        result = await session.execute(query)
        return result.scalars().first()


cafe_crud: CafeCRUD = CafeCRUD(Cafe)
