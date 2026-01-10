import uuid

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.cafe import CafeManagerLink


class CafeAccessCRUD:
    """Проверки прав на уровне CafeManagerLink (User ↔ Cafe)."""

    async def is_manager_of_cafe(
        self,
        session: AsyncSession,
        *,
        manager_id: uuid.UUID,
        cafe_id: uuid.UUID,
    ) -> bool:
        """Проверяет менеджер - кафе."""
        stmt = select(
            exists().where(
                CafeManagerLink.cafe_id == cafe_id,
                CafeManagerLink.user_id == manager_id,
                CafeManagerLink.is_active.is_(True),
            ),
        )
        return bool(await session.scalar(stmt))

    async def assert_manager_of_cafe(
        self,
        session: AsyncSession,
        *,
        manager_id: uuid.UUID,
        cafe_id: uuid.UUID,
        exc: Exception,
    ) -> None:
        """Выбрасывает исключение если менеджер не в кафе."""
        if not await self.is_manager_of_cafe(
            session,
            manager_id=manager_id,
            cafe_id=cafe_id,
        ):
            raise exc


cafe_access_crud: CafeAccessCRUD = CafeAccessCRUD()
