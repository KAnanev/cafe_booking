from typing import Any, Generic, Optional, Sequence, Type, TypeVar, Union

from pydantic import BaseModel
from sqlalchemy import inspect, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.selectable import Select

from core.db import Base
from models import User

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Базовый класс для CRUD."""

    def __init__(self, model: Type[ModelType]) -> None:
        """Инициализатор класса."""
        self.model = model

    def _apply_active_filter(self, query: Select, show_all: bool) -> Select:
        """Фильтрует по is_active, если модель это поддерживает."""
        if not show_all and hasattr(self.model, 'is_active'):
            query = query.where(self.model.is_active.is_(True))
        return query

    async def get_by_id(
        self,
        obj_id: Any,
        session: AsyncSession,
        show_all: bool = False,
    ) -> Optional[ModelType]:
        """Получает объект по его ID."""
        query = select(self.model).where(self.model.id == obj_id)
        query = self._apply_active_filter(query, show_all=show_all)

        db_obj = await session.execute(query)
        return db_obj.scalars().first()

    async def get_multi(
        self,
        session: AsyncSession,
        show_all: bool = False,
    ) -> Sequence[ModelType]:
        """Получает список объектов."""
        query = select(self.model)
        query = self._apply_active_filter(query, show_all=show_all)

        db_objs = await session.execute(query)
        return db_objs.scalars().all()

    async def create(
        self,
        obj_in: CreateSchemaType,
        session: AsyncSession,
        user: Optional[User] = None,
        commit: bool = True,
    ) -> ModelType:
        """Создаёт новый объект в базе данных."""
        model_columns = set(inspect(self.model).columns.keys())

        obj_in_data = obj_in.model_dump()
        filtered_data = {
            k: v for k, v in obj_in_data.items() if k in model_columns
        }

        if user is not None and 'user_id' in model_columns:
            filtered_data['user_id'] = user.id

        db_obj = self.model(**filtered_data)
        session.add(db_obj)
        if commit:
            await session.commit()
            await session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, dict],
        session: AsyncSession,
    ) -> ModelType:
        """Обновляет существующий объект."""
        model_columns = set(inspect(self.model).columns.keys())

        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        filtered_data = {
            k: v
            for k, v in update_data.items()
            if k in model_columns and v is not None
        }

        for field, value in filtered_data.items():
            setattr(db_obj, field, value)

        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def remove(
        self,
        db_obj: ModelType,
        session: AsyncSession,
    ) -> ModelType:
        """Искусственное удаление."""
        if hasattr(db_obj, 'is_active'):
            setattr(db_obj, 'is_active', False)
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
            return db_obj

        raise AttributeError(
            f'Объект {db_obj.__class__.__name__} не поддерживает удаление.',
        )
