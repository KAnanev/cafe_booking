from __future__ import annotations

import uuid
from typing import Any, Generic, Mapping, Optional, Type, TypeVar, Union

from pydantic import BaseModel
from sqlalchemy import exists, inspect, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from core.db import Base

ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Базовый CRUD."""

    def __init__(self, model: Type[ModelType]) -> None:
        """Сохраняет модель и кеширует список её колонок."""
        self._model: Type[ModelType] = model
        self._model_columns: set[str] = set(
            inspect(self._model).columns.keys(),
        )

    def _select_base(self) -> Select[tuple[ModelType]]:
        """Базовый SELECT по модели."""
        return select(self._model)

    def _apply_only_active(
        self,
        query: Select[Any],
        *,
        only_active: bool,
    ) -> Select[Any]:
        """Опционально добавляет фильтр is_active=True, если колонка есть."""
        if only_active and hasattr(self._model, 'is_active'):
            return query.where(self._model.is_active.is_(True))  # type: ignore[attr-defined]
        return query

    async def list(
        self,
        session: AsyncSession,
        *,
        only_active: bool = True,
        query: Optional[Select[Any]] = None,
    ) -> list[ModelType]:
        """Возвращает список объектов (по умолчанию только активные)."""
        q: Select[Any] = query or self._select_base()
        q = self._apply_only_active(q, only_active=only_active)
        res = await session.execute(q)
        return list(res.scalars().all())

    async def get(
        self,
        session: AsyncSession,
        *,
        obj_id: Any,
        only_active: bool = True,
        query: Optional[Select[Any]] = None,
    ) -> Optional[ModelType]:
        """Возвращает объект по id или None (по умолчанию только активный)."""
        if query is None:
            query = self._select_base().where(self._model.id == obj_id)  # type: ignore[attr-defined]

        q = self._apply_only_active(query, only_active=only_active)
        res = await session.execute(q)
        return res.scalars().first()

    def _build_create_data(
        self,
        *,
        obj_in: Union[CreateSchemaType, Mapping[str, Any]],
        user_id: Optional[uuid.UUID] = None,
        extra_data: Optional[Mapping[str, Any]] = None,
    ) -> dict[str, Any]:
        """Готовит данные для создания: obj_in + extra_data."""
        data = obj_in.model_dump(exclude_unset=True)

        if extra_data:
            data.update(extra_data)

        filtered: dict[str, Any] = {
            k: v for k, v in data.items() if k in self._model_columns
        }

        if user_id is not None and 'user_id' in self._model_columns:
            filtered['user_id'] = user_id

        return filtered

    async def _create_from_data(
        self,
        session: AsyncSession,
        *,
        data: Mapping[str, Any],
    ) -> ModelType:
        """Создаёт объект."""
        db_obj: ModelType = self._model(**dict(data))  # type: ignore[arg-type]
        session.add(db_obj)
        await session.flush()
        await session.refresh(db_obj)
        return db_obj

    async def create(
        self,
        session: AsyncSession,
        *,
        obj_in: CreateSchemaType,
        user_id: Optional[uuid.UUID] = None,
    ) -> ModelType:
        """Создает без связей."""
        data = self._build_create_data(obj_in=obj_in, user_id=user_id)
        return await self._create_from_data(session, data=data)

    async def create_for_parent(
        self,
        session: AsyncSession,
        *,
        parent_field: str,
        parent_id: uuid.UUID,
        obj_in: Union[CreateSchemaType, Mapping[str, Any]],
        user_id: Optional[uuid.UUID] = None,
    ) -> ModelType:
        """Создает со связями."""
        data = self._build_create_data(
            obj_in=obj_in,
            user_id=user_id,
            extra_data={parent_field: parent_id},
        )
        return await self._create_from_data(session, data=data)

    async def update(
        self,
        session: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Mapping[str, Any]],
    ) -> ModelType:
        """Обновляет объект данными."""
        if isinstance(obj_in, Mapping):
            update_data: Mapping[str, Any] = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if field in self._model_columns:
                setattr(db_obj, field, value)

        await session.flush()
        await session.refresh(db_obj)
        return db_obj

    async def exists_by_id(
        self,
        session: AsyncSession,
        *,
        model: Type[Base],
        obj_id: uuid.UUID,
    ) -> bool:
        """Проверяет существование по id."""
        stmt = select(exists().where(model.id == obj_id))
        return bool(await session.scalar(stmt))
