from datetime import time
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase
from models.slot import Slot
from schemas.slot import SlotCreate, SlotUpdate


class SlotCRUD(CRUDBase[Slot, SlotCreate, SlotUpdate]):
    """CRUD для временных слотов."""

    async def exists_slot(
        self,
        session: AsyncSession,
        cafe_id: UUID,
        start: time,
        end: time,
        exclude_id: UUID | None = None,
    ) -> bool:
        """Проверить существование активного слота с указанными параметрами."""
        conditions = [
            self._model.cafe_id == cafe_id,
            self._model.start_time == start,
            self._model.end_time == end,
            self._model.is_active.is_(True),
        ]
        if exclude_id is not None:
            conditions.append(self._model.id != exclude_id)

        query = (
            select(func.count())
            .select_from(self._model)
            .where(and_(*conditions))
        )
        result = await session.execute(query)
        count_value = result.scalar_one()
        return count_value > 0

    async def create(
        self,
        obj_in: SlotCreate,
        session: AsyncSession,
        related: dict[str, list] | None = None,
    ) -> Slot:
        """Создать новый временной слот."""
        return await super().create(obj_in=obj_in, session=session)

    async def update(
        self,
        db_obj: Slot,
        obj_in: SlotUpdate,
        session: AsyncSession,
        related: dict[str, list] | None = None,
    ) -> Slot:
        """Обновить слот с проверкой корректности временного интервала."""
        start = obj_in.start_time or db_obj.start_time
        end = obj_in.end_time or db_obj.end_time

        if start >= end:
            raise ValueError(
                'Начальное время не может быть больше или равно конечному',
            )

        return await super().update(
            db_obj=db_obj,
            obj_in=obj_in,
            session=session,
        )


slot_crud = SlotCRUD(Slot)
