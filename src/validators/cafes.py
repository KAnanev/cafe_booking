from http import HTTPStatus
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_async_session
from crud.cafe import cafe_crud
from models.cafe import Cafe


async def get_cafe_or_404(
    cafe_id: UUID,
    session: AsyncSession = Depends(get_async_session),
) -> Cafe:
    """Получает кафе по ID или отдаёт 404."""
    cafe = await cafe_crud.get_by_id(
        obj_id=cafe_id,
        session=session,
        show_all=False,
    )
    if cafe is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Кафе не найдено',
        )
    return cafe
