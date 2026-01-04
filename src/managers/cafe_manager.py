from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from crud.cafe import cafe_crud
from managers.exceptions import CafeNotFound, PermissionDenied
from models.cafe import Cafe
from models.user import User, UserRole
from schemas.cafe import CafeCreate, CafeUpdate


class CafeManager:
    """Менеджер кафе: бизнес-логика и оркестрация операций с кафе."""

    def __init__(self, session: AsyncSession) -> None:
        """Сохранить сессию БД для выполнения операций."""
        self._session = session

    async def list_cafes(self, show_all: bool) -> list[Cafe]:
        """Вернуть список кафе (при show_all=True включая неактивные)."""
        query = select(Cafe)
        if not show_all:
            query = query.where(Cafe.is_active.is_(True))

        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def get_cafe(self, cafe_id: UUID) -> Cafe:
        """Вернуть кафе по идентификатору или выбросить CafeNotFound."""
        cafe = await cafe_crud.get_by_id(
            obj_id=cafe_id,
            session=self._session,
        )
        if cafe is None:
            raise CafeNotFound('Кафе не найдено')
        return cafe

    async def create_cafe(
        self,
        cafe_in: CafeCreate,
        current_user: User,
    ) -> Cafe:
        """Создать кафе и применить бизнес-правило назначения менеджера."""
        if current_user.role not in (UserRole.MANAGER, UserRole.ADMIN):
            raise PermissionDenied('Нет прав для создания кафе')

        cafe = await cafe_crud.create(
            obj_in=cafe_in,
            session=self._session,
        )

        if current_user.role == UserRole.MANAGER:
            cafe.managers.append(current_user)
            await self._session.flush()
            await self._session.refresh(cafe)
        return cafe

    async def update_cafe(
        self,
        cafe_id: UUID,
        cafe_in: CafeUpdate,
        current_user: User,
    ) -> Cafe:
        """Обновить кафе с проверкой прав доступа."""
        cafe = await self.get_cafe(cafe_id=cafe_id)

        if current_user.role == UserRole.ADMIN:
            pass
        elif current_user.role == UserRole.MANAGER:
            manager_ids = {manager.id for manager in cafe.managers}
            if current_user.id not in manager_ids:
                raise PermissionDenied('Нет прав для изменения кафе')
        else:
            raise PermissionDenied('Нет прав для изменения кафе')

        return await cafe_crud.update(
            db_obj=cafe,
            obj_in=cafe_in,
            session=self._session,
        )
