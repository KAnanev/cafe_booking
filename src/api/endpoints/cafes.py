from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from api.dependencies.auth import (
    require_admin,
    require_admin_or_manager,
    require_auth,
)
from api.dependencies.managers import (
    get_cafe_manager,
)
from managers.cafe_manager import CafeManager
from models.user import User
from schemas.cafe import CafeCreate, CafeRead, CafeUpdate

router = APIRouter()


@router.get(
    '',
    response_model=list[CafeRead],
    status_code=status.HTTP_200_OK,
    summary='Получение списка кафе.',
)
async def get_cafes(
    show_all: bool = Query(
        True,
        description='Показывать все кафе или нет.'
        'По умолчанию показывает все кафе',
    ),
    user: User = require_auth,
    cafe_manager: CafeManager = Depends(get_cafe_manager),
) -> Sequence[CafeRead]:
    """Получение списка кафе.

    Для администраторов и менеджеров - все кафе (с возможностью выбора),
    для пользователей - только активные.
    """
    cafes = await cafe_manager.list(show_all=show_all, user=user)
    return [CafeRead.model_validate(cafe) for cafe in cafes]


@router.post(
    '',
    response_model=CafeRead,
    status_code=status.HTTP_201_CREATED,
    summary='Создание нового кафе',
)
async def create_cafe(
    cafe_in: CafeCreate,
    user: User = require_admin,
    cafe_manager: CafeManager = Depends(get_cafe_manager),
) -> CafeRead:
    """Создает новое кафе.

    Только для администраторов и ???менеджеров???
    """
    cafe = await cafe_manager.create(obj_in=cafe_in, user_id=user.id)
    return CafeRead.model_validate(cafe)


@router.get(
    '/{cafe_id}',
    response_model=CafeRead,
    status_code=status.HTTP_200_OK,
    summary='Получение информации о кафе по его ID',
)
async def get_cafe(
    cafe_id: UUID,
    user: User = require_auth,
    cafe_manager: CafeManager = Depends(get_cafe_manager),
) -> CafeRead:
    """Получение информации о кафе по его ID.

    Для администраторов и менеджеров - все кафе,
    для пользователей - только активные.
    """
    cafe = await cafe_manager.get(cafe_id=cafe_id, user=user)
    return CafeRead.model_validate(cafe)


@router.patch(
    '/{cafe_id}',
    response_model=CafeRead,
    status_code=status.HTTP_200_OK,
    summary='Обновление информации о кафе по его ID',
)
async def update_cafe(
    cafe_id: UUID,
    cafe_in: CafeUpdate,
    user: User = require_admin_or_manager,
    cafe_manager: CafeManager = Depends(get_cafe_manager),
) -> CafeRead:
    """Обновление информации о кафе по его ID.

    Только для администраторов и менеджеров.
    """
    cafe = await cafe_manager.update(
        user=user,
        cafe_id=cafe_id,
        obj_in=cafe_in,
    )
    return CafeRead.model_validate(cafe)
