from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.permissions import can_manage_cafe
from core.db import get_async_session
from crud.slots import slot_crud
from models.cafe import Cafe
from models.user import User
from schemas.slot import SlotCreate, SlotRead, SlotUpdate
from validators.cafes import get_cafe_or_404

router = APIRouter()


@router.get(
    '',
    response_model=Sequence[SlotRead],
    summary='Получить слоты кафе',
)
async def get_slots(
    show_all: bool = Query(
        False,
        description='Показывать неактивные слоты',
    ),
    session: AsyncSession = Depends(get_async_session),
    cafe: Cafe = Depends(get_cafe_or_404),
) -> Sequence[SlotRead]:
    """Получить список временных слотов для указанного кафе."""
    query = select(slot_crud.model).where(
        slot_crud.model.cafe_id == cafe.id,
    )
    if not show_all:
        query = query.where(slot_crud.model.is_active.is_(True))

    result = await session.execute(query)
    return result.scalars().all()


@router.post(
    '',
    response_model=SlotRead,
    status_code=status.HTTP_201_CREATED,
    summary='Создать слот',
)
async def create_slot(
    slot_in: SlotCreate,
    session: AsyncSession = Depends(get_async_session),
    cafe: Cafe = Depends(get_cafe_or_404),
    current_user: User = Depends(can_manage_cafe),
) -> SlotRead:
    """Создать новый временной слот для указанного кафе."""
    if slot_in.cafe_id != cafe.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='cafe_id в теле не совпадает с cafe_id в пути',
        )
    try:
        return await slot_crud.create(obj_in=slot_in, session=session)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.patch(
    '/{slot_id}',
    response_model=SlotRead,
    summary='Обновить слот',
)
async def update_slot(
    slot_id: UUID,
    slot_in: SlotUpdate,
    session: AsyncSession = Depends(get_async_session),
    cafe: Cafe = Depends(get_cafe_or_404),
    current_user: User = Depends(can_manage_cafe),
) -> SlotRead:
    """Обновить данные слота."""
    slot = await slot_crud.get_by_id(slot_id, session=session)
    if slot is None or slot.cafe_id != cafe.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Слот не найден',
        )
    if slot_in.cafe_id is not None:
        if slot_in.cafe_id != cafe.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='cafe_id в теле не совпадает с cafe_id в пути',
            )
        slot_in.cafe_id = None

    try:
        return await slot_crud.update(
            db_obj=slot, obj_in=slot_in, session=session)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
