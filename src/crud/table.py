from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase
from models.table import Table
from schemas.table import TableCreate, TableUpdate


class TableCRUD(CRUDBase[Table, TableCreate, TableUpdate]):
    """CRUD для столов."""

    async def get_by_cafe(
        self,
        session: AsyncSession,
        cafe_id: UUID,
        show_all: bool = False,
    ) -> Sequence[Table]:
        query = select(self.model).where(self.model.cafe_id == cafe_id)
        if not show_all:
            query = query.where(self.model.is_active.is_(True))
        result = await session.execute(query)
        return result.scalars().all()

    async def get_by_cafe_and_id(
        self,
        session: AsyncSession,
        cafe_id: UUID,
        table_id: UUID,
        show_all: bool = False,
    ) -> Table | None:
        query = select(self.model).where(
            self.model.id == table_id,
            self.model.cafe_id == cafe_id,
        )
        if not show_all:
            query = query.where(self.model.is_active.is_(True))
        result = await session.execute(query)
        return result.scalars().first()


table_crud = TableCRUD(Table)
