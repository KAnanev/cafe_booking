from typing import List, Sequence, Union
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase
from models.dishes import Dish, DishCafeLink
from schemas.dishes import DishCreate, DishUpdate


class DishCRUD(CRUDBase[Dish, DishCreate, DishUpdate]):
    """CRUD для блюд с управлением связями с кафе."""

    async def create(
        self,
        obj_in: DishCreate,
        session: AsyncSession,
        commit: bool = True,
    ) -> Dish:
        dish_data = obj_in.model_dump(exclude={'cafes_id'})
        
        db_obj = self.model(**dish_data)
        session.add(db_obj)
        await session.flush()
        
        await self._save_cafe_links(db_obj, obj_in.cafes_id, session)
        
        if commit:
            await session.commit()
            await session.refresh(db_obj)
            
        return db_obj

    async def update(
        self,
        db_obj: Dish,
        obj_in: Union[DishUpdate, dict],
        session: AsyncSession,
    ) -> Dish:
        await super().update(db_obj, obj_in, session)

        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump()
        
        if update_data.get('cafes_id') is not None:
            await self._update_cafe_links(db_obj, update_data['cafes_id'], session)
        
        await session.commit()
        await session.refresh(db_obj)
        return db_obj
    
    async def get_all(
        self,
        session: AsyncSession,
        show_all: bool = False,
        cafe_id: UUID | None = None,
    ) -> Sequence[Dish]:
        """Получить список блюд, с опциональной фильтрацией по кафе."""
        query = select(self.model)
        
        if cafe_id:
            query = query.join(DishCafeLink).where(DishCafeLink.cafe_id == cafe_id)

        if not show_all:
            query = query.where(self.model.is_active.is_(True))
            
        result = await session.execute(query)
        return result.scalars().all()


    async def _save_cafe_links(self, dish: Dish, cafe_ids: List[UUID], session: AsyncSession):
        """Создает новые связи между блюдом и кафе."""
        for cafe_id in cafe_ids:
            link = DishCafeLink(dish_id=dish.id, cafe_id=cafe_id)
            session.add(link)

    async def _update_cafe_links(self, dish: Dish, new_cafe_ids: List[UUID], session: AsyncSession):
        """Удаляет старые связи и создает новые."""
        # 1. Удаляем старые связи
        await session.execute(
            DishCafeLink.__table__.delete().where(DishCafeLink.dish_id == dish.id)
        )
        # 2. Создаем новые
        await self._save_cafe_links(dish, new_cafe_ids, session)


dish_crud = DishCRUD(Dish)