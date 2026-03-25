import uuid
from typing import Optional

from sqlalchemy import Select, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase
from models.cafe import Cafe, CafeManagerLink
from schemas.cafe import CafeCreate, CafeUpdate


class CafeCRUD(CRUDBase[Cafe, CafeCreate, CafeUpdate]):
    """CRUD для кафе."""

    def _query_for_manager(self, *, manager_id: uuid.UUID) -> Select:
        """Строит запрос на выборку кафе, доступных конкретному менеджеру."""
        return (
            self
            ._select_base()
            .join(CafeManagerLink, CafeManagerLink.cafe_id == self._model.id)
            .where(CafeManagerLink.user_id == manager_id)
            .where(CafeManagerLink.is_active.is_(True))
        ).distinct()

    async def list_for_user(self, session: AsyncSession) -> list[Cafe]:
        """Возвращает список кафе, для пользователей."""
        return await self.list(session, only_active=True)

    async def list_for_manager(
        self,
        session: AsyncSession,
        *,
        manager_id: uuid.UUID,
        only_active: bool = True,
    ) -> list[Cafe]:
        """Возвращает список кафе, которыми управляет менеджер."""
        query = self._query_for_manager(manager_id=manager_id)
        return await self.list(session, only_active=only_active, query=query)

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
        ).where(self._model.id == obj_id)
        return await self.get(
            session,
            obj_id=obj_id,
            only_active=only_active,
            query=query,
        )

    async def _create_manager_links(
        self,
        session: AsyncSession,
        *,
        cafe: Cafe,
        managers: set[uuid.UUID],
    ) -> None:
        if not managers:
            return
        session.add_all([
            CafeManagerLink(cafe=cafe, user_id=uid) for uid in managers
        ])
        await session.flush()

    async def create(
        self,
        session: AsyncSession,
        *,
        obj_in: CafeCreate,
        user_id: Optional[uuid.UUID] = None,
    ) -> Cafe:
        """Создает кафе."""
        data = obj_in.model_dump(exclude={'managers_id'})
        cafe = await super().create(session, obj_in=data, user_id=user_id)

        await self._create_manager_links(
            session,
            cafe=cafe,
            managers=set(obj_in.managers_id),
        )
        await session.refresh(cafe)
        return cafe

    async def sync_managers(
        self,
        session: AsyncSession,
        *,
        cafe: Cafe,
        managers_id: list[uuid.UUID],
    ) -> None:
        """Синхронизирует менеджеров."""
        new_set = set(managers_id)

        res = await session.execute(
            select(CafeManagerLink).where(
                CafeManagerLink.cafe == cafe,
                or_(
                    CafeManagerLink.is_active.is_(True),
                    CafeManagerLink.user_id.in_(new_set),
                ),
            ),
        )
        links = list(res.scalars().all())
        by_user = {link.user_id: link for link in links}

        for link in links:
            if link.is_active and link.user_id not in new_set:
                link.is_active = False

        for uid in new_set:
            link = by_user.get(uid)
            if link is not None and not link.is_active:
                link.is_active = True

        missing = new_set - set(by_user.keys())
        await self._create_manager_links(session, cafe=cafe, managers=missing)

        await session.flush()

    async def update(
        self,
        session: AsyncSession,
        *,
        db_obj: Cafe,
        obj_in: CafeUpdate,
    ) -> Cafe:
        """Обновляет кафе."""
        data = obj_in.model_dump(exclude_unset=True)

        managers_id = data.pop('managers_id', None)

        cafe = await super().update(session, db_obj=db_obj, obj_in=data)

        if managers_id is not None:
            await self.sync_managers(
                session,
                cafe=cafe,
                managers_id=managers_id,
            )

        await session.refresh(cafe)
        return cafe


cafe_crud: CafeCRUD = CafeCRUD(Cafe)
