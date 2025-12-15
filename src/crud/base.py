from typing import Generic, Optional, Sequence, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import inspect, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import Base
from models import User

ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Базовый класс для CRUD."""

    def __init__(self, model: Type[ModelType]) -> None:
        """Инициализатор класса."""
        self.model = model

    async def get_by_id(
        self,
        obj_id: int,
        session: AsyncSession,
    ) -> Optional[ModelType]:
        """Получает объект по его ID."""
        db_obj = await session.execute(
            select(self.model).where(self.model.id == obj_id),
        )
        return db_obj.scalars().first()

    async def get_multi(self, session: AsyncSession) -> Sequence[ModelType]:
        """Получает список всех объектов."""
        db_objs = await session.execute(select(self.model))
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
        obj_in: UpdateSchemaType,
        session: AsyncSession,
    ) -> ModelType:
        """Обновляет существующий объект в базе данных."""
        obj_data = obj_in.dict(exclude_unset=True)

        for field in obj_data:
            if field in obj_data:
                setattr(db_obj, field, obj_data[field])
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
