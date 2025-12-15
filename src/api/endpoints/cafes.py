from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.permissions import can_manage_cafe, is_manager_or_admin
from core.db import get_async_session
from crud.cafe import cafe_crud
from models.user import Roles, User
from schemas.cafe import CafeCreate, CafeRead, CafeUpdate

router = APIRouter()


@router.get(
    '',
    response_model=Sequence[CafeRead],
    summary='Получить список кафе',
)
async def get_cafes(
    show_all: bool = Query(
        False,
        description='Показывать неактивные кафе тоже',
    ),
    session: AsyncSession = Depends(get_async_session),
) -> Sequence[CafeRead]:
    """Получить список всех кафе."""
    return await cafe_crud.get_all(session=session, show_all=show_all)


@router.post(
    '',
    response_model=CafeRead,
    status_code=status.HTTP_201_CREATED,
    summary='Создать кафе',
)
async def create_cafe(
    cafe_in: CafeCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(is_manager_or_admin),
) -> CafeRead:
    """Создать кафе."""
    cafe = await cafe_crud.create(
        obj_in=cafe_in,
        session=session,
        commit=False,
    )
    await session.flush()
    if current_user.role == Roles.MANAGER:
        cafe.managers.append(current_user)
    await session.commit()
    await session.refresh(cafe)
    return cafe


@router.get(
    '/{cafe_id}',
    response_model=CafeRead,
    summary='Получить кафе по ID',
)
async def get_cafe(
    cafe_id: UUID,
    session: AsyncSession = Depends(get_async_session),
) -> CafeRead:
    """Получить информацию о кафе по его идентификатору."""
    cafe = await cafe_crud.get_by_id(obj_id=cafe_id, session=session)
    if cafe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Кафе не найдено',
        )
    return cafe


@router.patch(
    '/{cafe_id}',
    response_model=CafeRead,
    summary='Обновить кафе',
)
async def update_cafe(
    cafe_id: UUID,
    cafe_in: CafeUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(can_manage_cafe),
) -> CafeRead:
    """Обновить информацию о кафе."""
    cafe = await cafe_crud.get_by_id(obj_id=cafe_id, session=session)
    if cafe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Кафе не найдено',
        )
    return await cafe_crud.update(db_obj=cafe, obj_in=cafe_in, session=session)
