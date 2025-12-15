from datetime import time
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase
from models.slots import Slot
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
            self.model.cafe_id == cafe_id,
            self.model.start_time == start,
            self.model.end_time == end,
            self.model.is_active.is_(True),
        ]
        if exclude_id is not None:
            conditions.append(self.model.id != exclude_id)

        query = select(self.model.id).where(and_(*conditions))
        result = await session.execute(query)
        return result.scalars().first() is not None

    async def create(
        self,
        obj_in: SlotCreate,
        session: AsyncSession,
        related: dict[str, list] | None = None,
    ) -> Slot:
        """Создать новый временной слот с проверкой на уникальность."""
        if await self.exists_slot(
            session=session,
            cafe_id=obj_in.cafe_id,
            start=obj_in.start_time,
            end=obj_in.end_time,
        ):
            raise ValueError(
                'Слот с таким временем уже существует для этого кафе',
            )
        return await super().create(obj_in=obj_in, session=session)

    async def update(
        self,
        db_obj: Slot,
        obj_in: SlotUpdate,
        session: AsyncSession,
        related: dict[str, list] | None = None,
    ) -> Slot:
        """Обновить слот с проверкой корректности данных."""
        start = obj_in.start_time or db_obj.start_time
        end = obj_in.end_time or db_obj.end_time
        cafe_id = obj_in.cafe_id or db_obj.cafe_id

        if start >= end:
            raise ValueError(
                'Начальное время не может быть больше или равно конечному',
            )

        if await self.exists_slot(
            session=session,
            cafe_id=cafe_id,
            start=start,
            end=end,
            exclude_id=db_obj.id,
        ):
            raise ValueError(
                'Слот с таким временем уже существует для этого кафе',
            )
        return await super().update(
            db_obj=db_obj,
            obj_in=obj_in,
            session=session,
        )


slot_crud = SlotCRUD(Slot)
