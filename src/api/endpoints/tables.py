import uuid

from fastapi import APIRouter, Depends, Query, status

from api.dependencies.auth import require_admin_or_manager, require_auth
from api.dependencies.managers import get_table_manager
from managers.table_manager import TableManager
from models.user import User
from schemas.table import TableCreate, TableRead, TableUpdate

router = APIRouter()


@router.get(
    '',
    response_model=list[TableRead],
    summary='Получить список столов в кафе',
)
async def get_tables(
    cafe_id: uuid.UUID,
    show_all: bool = Query(
        True,
        description='Показывать все столы в кафе или нет. '
        'По умолчанию показывает все столы',
    ),
    user: User = Depends(require_auth),
    table_manager: TableManager = Depends(get_table_manager),
) -> list[TableRead]:
    """Получить столы кафе."""
    tables = await table_manager.list(
        user=user,
        cafe_id=cafe_id,
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
    cafe_id: uuid.UUID,
    table_in: TableCreate,
    user: User = Depends(require_admin_or_manager),
    table_manager: TableManager = Depends(get_table_manager),
) -> TableRead:
    """Создать новый стол в указанном кафе."""
    table = await table_manager.create(
        cafe_id=cafe_id,
        obj_in=table_in,
        user=user,
    )
    return TableRead.model_validate(table)


@router.get(
    '/{table_id}',
    response_model=TableRead,
    summary='Получить стол по ID',
)
async def get_table(
    cafe_id: uuid.UUID,
    table_id: uuid.UUID,
    user: User = Depends(require_auth),
    table_manager: TableManager = Depends(get_table_manager),
) -> TableRead:
    """Получить информацию о конкретном столе в указанном кафе."""
    table = await table_manager.get(
        cafe_id=cafe_id,
        table_id=table_id,
        user=user,
    )
    return TableRead.model_validate(table)


@router.patch(
    '/{table_id}',
    response_model=TableRead,
    summary='Обновить стол',
)
async def update_table(
    cafe_id: uuid.UUID,
    table_id: uuid.UUID,
    table_in: TableUpdate,
    user: User = Depends(require_admin_or_manager),
    table_manager: TableManager = Depends(get_table_manager),
) -> TableRead:
    """Обновить информацию о столе в указанном кафе."""
    table = await table_manager.update(
        cafe_id=cafe_id,
        table_id=table_id,
        obj_in=table_in,
        user=user,
    )
    return TableRead.model_validate(table)
