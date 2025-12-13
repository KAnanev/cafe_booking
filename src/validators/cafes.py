from http import HTTPStatus
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_async_session
from models.cafe import Cafe


async def get_cafe_or_404(
    cafe_id: UUID,
    session: AsyncSession = Depends(get_async_session),
) -> Cafe:
    """Получает кафе по ID или отдаёт 404."""
    stmt = select(Cafe).where(
        Cafe.id == cafe_id,
        Cafe.is_active.is_(True),
    )
    result = await session.execute(stmt)
    cafe = result.scalars().first()
    if cafe is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Кафе не найдено',
        )
    return cafe
