from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from api.dependencies.auth import require_admin_or_manager
from api.dependencies.managers import get_table_manager
from managers.table_manager import TableManager
from models.cafe import Cafe
from models.user import User
from schemas.table import TableCreate, TableRead, TableUpdate
from validators.cafes import get_cafe_or_404

router = APIRouter()


@router.get(
    '',
    response_model=list[TableRead],
    summary='Получить список столов в кафе',
)
async def get_tables(
    show_all: bool = Query(False, description='Показывать неактивные столы'),
    cafe: Cafe = Depends(get_cafe_or_404),
    table_manager: TableManager = Depends(get_table_manager),
) -> list[TableRead]:
    """Получить столы кафе."""
    tables = await table_manager.list_tables(
        cafe_id=cafe.id,
        show_all=show_all,
    )
    return [TableRead.model_validate(table) for table in tables]


@router.post(
    '',
    response_model=TableRead,
    status_code=status.HTTP_201_CREATED,
    summary='Создать стол в кафе',
)
async def create_table(
    table_in: TableCreate,
    cafe: Cafe = Depends(get_cafe_or_404),
    current_user: User = require_admin_or_manager,
    table_manager: TableManager = Depends(get_table_manager),
) -> TableRead:
    """Создать новый стол в указанном кафе."""
    table = await table_manager.create_table(
        cafe_id=cafe.id,
        table_in=table_in,
        current_user=current_user,
    )
    return TableRead.model_validate(table)


@router.get(
    '/{table_id}',
    response_model=TableRead,
    summary='Получить стол по ID',
)
async def get_table(
    table_id: UUID,
    cafe: Cafe = Depends(get_cafe_or_404),
    table_manager: TableManager = Depends(get_table_manager),
) -> TableRead:
    """Получить информацию о конкретном столе в указанном кафе."""
    table = await table_manager.get_table(
        cafe_id=cafe.id,
        table_id=table_id,
    )
    return TableRead.model_validate(table)


@router.patch(
    '/{table_id}',
    response_model=TableRead,
    summary='Обновить стол',
)
async def update_table(
    table_id: UUID,
    table_in: TableUpdate,
    cafe: Cafe = Depends(get_cafe_or_404),
    current_user: User = require_admin_or_manager,
    table_manager: TableManager = Depends(get_table_manager),
) -> TableRead:
    """Обновить информацию о столе в указанном кафе."""
    table = await table_manager.update_table(
        cafe_id=cafe.id,
        table_id=table_id,
        table_in=table_in,
        current_user=current_user,
    )
    return TableRead.model_validate(table)
