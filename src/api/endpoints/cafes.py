from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from api.dependencies.auth import require_admin_or_manager
from api.dependencies.managers import get_cafe_manager
from managers.cafe_manager import CafeManager
from models.user import User
from schemas.cafe import CafeCreate, CafeRead, CafeUpdate

router = APIRouter()


@router.get(
    '',
    response_model=Sequence[CafeRead],
    summary='Получить список кафе',
)
async def get_cafes(
    show_all: bool = Query(False, description='Показывать неактивные кафе'),
    cafe_manager: CafeManager = Depends(get_cafe_manager),
) -> Sequence[CafeRead]:
    """Получить список всех кафе."""
    cafes = await cafe_manager.list_cafes(show_all=show_all)
    return [CafeRead.model_validate(cafe) for cafe in cafes]


@router.post(
    '',
    response_model=CafeRead,
    status_code=status.HTTP_201_CREATED,
    summary='Создать кафе',
)
async def create_cafe(
    cafe_in: CafeCreate,
    current_user: User = require_admin_or_manager,
    cafe_manager: CafeManager = Depends(get_cafe_manager),
) -> CafeRead:
    """Создать кафе."""
    cafe = await cafe_manager.create_cafe(
        cafe_in=cafe_in,
        current_user=current_user,
    )
    return CafeRead.model_validate(cafe)


@router.get(
    '/{cafe_id}',
    response_model=CafeRead,
    summary='Получить кафе по ID',
)
async def get_cafe(
    cafe_id: UUID,
    cafe_manager: CafeManager = Depends(get_cafe_manager),
) -> CafeRead:
    """Получить информацию о кафе по его идентификатору."""
    cafe = await cafe_manager.get_cafe(cafe_id=cafe_id)
    return CafeRead.model_validate(cafe)


@router.patch(
    '/{cafe_id}',
    response_model=CafeRead,
    summary='Обновить кафе',
)
async def update_cafe(
    cafe_id: UUID,
    cafe_in: CafeUpdate,
    current_user: User = require_admin_or_manager,
    cafe_manager: CafeManager = Depends(get_cafe_manager),
) -> CafeRead:
    """Обновить информацию о кафе."""
    cafe = await cafe_manager.update_cafe(
        cafe_id=cafe_id,
        cafe_in=cafe_in,
        current_user=current_user,
    )
    return CafeRead.model_validate(cafe)
