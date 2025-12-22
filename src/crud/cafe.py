from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from crud.base import CRUDBase
from models.cafe import Cafe
from schemas.cafe import CafeCreate, CafeUpdate


class CafeCRUD(CRUDBase[Cafe, CafeCreate, CafeUpdate]):
    """CRUD для кафе."""

    async def get_managed_cafes(
        self,
        session: AsyncSession,
        user_id: UUID,
        show_all: bool = False,
    ) -> Sequence[Cafe]:
        """Кафе, которыми управляет пользователь."""
        query = (
            select(self.model)
            .options(selectinload(self.model.managers))
            .where(self.model.managers.any(id=user_id))
        )
        query = self._apply_active_filter(query, show_all=show_all)

        result = await session.execute(query)
        return result.scalars().all()


cafe_crud = CafeCRUD(Cafe)
