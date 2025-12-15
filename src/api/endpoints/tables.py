from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.permissions import can_manage_cafe
from core.db import get_async_session
from crud.table import table_crud
from models.cafe import Cafe
from models.user import User
from schemas.table import TableCreate, TableRead, TableUpdate
from validators.cafes import get_cafe_or_404

router = APIRouter()


@router.get(
    '',
    response_model=Sequence[TableRead],
    summary='Получить список столов в кафе',
)
async def get_tables(
    show_all: bool = Query(
        False,
        description='Показывать неактивные столы',
    ),
    session: AsyncSession = Depends(get_async_session),
    cafe: Cafe = Depends(get_cafe_or_404),
) -> Sequence[TableRead]:
    """Получить столы кафе."""
    return await table_crud.get_by_cafe(
        session=session,
        cafe_id=cafe.id,
        show_all=show_all,
    )


@router.post(
    '',
    response_model=TableRead,
    status_code=status.HTTP_201_CREATED,
    summary='Создать стол в кафе',
)
async def create_table(
    table_in: TableCreate,
    session: AsyncSession = Depends(get_async_session),
    cafe: Cafe = Depends(get_cafe_or_404),
    current_user: User = Depends(can_manage_cafe),
) -> TableRead:
    """Создать новый стол в указанном кафе."""
    if table_in.cafe_id != cafe.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='cafe_id в теле не совпадает с cafe_id в пути',
        )

    return await table_crud.create(obj_in=table_in, session=session)


@router.get(
    '/{table_id}',
    response_model=TableRead,
    summary='Получить стол по ID',
)
async def get_table(
    table_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    cafe: Cafe = Depends(get_cafe_or_404),
) -> TableRead:
    """Получить информацию о конкретном столе в указанном кафе."""
    table = await table_crud.get_by_cafe_and_id(
        session=session,
        cafe_id=cafe.id,
        table_id=table_id,
        show_all=True,
    )
    if table is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Стол не найден',
        )
    return table


@router.patch(
    '/{table_id}',
    response_model=TableRead,
    summary='Обновить стол',
)
async def update_table(
    table_id: UUID,
    table_in: TableUpdate,
    session: AsyncSession = Depends(get_async_session),
    cafe: Cafe = Depends(get_cafe_or_404),
    current_user: User = Depends(can_manage_cafe),
) -> TableRead:
    """Обновить информацию о столе в указанном кафе."""
    table = await table_crud.get_by_cafe_and_id(
        session=session,
        cafe_id=cafe.id,
        table_id=table_id,
        show_all=True,
    )
    if table is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Стол не найден',
        )
    if table_in.cafe_id is not None:
        if table_in.cafe_id != cafe.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='cafe_id в теле не совпадает с cafe_id в пути',
            )
        table_in.cafe_id = None

    return await table_crud.update(db_obj=table, session=session)
