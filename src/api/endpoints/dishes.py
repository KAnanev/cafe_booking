from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.permissions import is_manager_or_admin
from api.dependencies.users import get_current_active_user
from api.utils import build_dish_response
from core.db import get_async_session
from crud.dishes import dish_crud
from models.dishes import Dish
from models.user import User, UserRole
from schemas.dishes import DishCreate, DishRead, DishUpdate

router = APIRouter()


def build_dish_response(dish: Dish) -> DishRead:
    """Формирует ответ по блюду согласно схеме DishRead."""
    return DishRead.model_validate(dish, from_attributes=True)


async def _get_dish_or_404(
    dish_id: UUID,
    session: AsyncSession,
) -> 'Dish':
    dish = await dish_crud.get_by_id(obj_id=dish_id, session=session)
    if dish is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Блюдо не найдено.')
    return dish


@router.get(
    '/',
    response_model=List[DishRead],
    summary='Получить список блюд',
)
async def get_dishes(
    show_all: bool = Query(False, description='Показывать неактивные блюда'),
    cafe_id: UUID | None = Query(None, description='Фильтр по ID кафе'),
    session: AsyncSession = Depends(get_async_session),
) -> List[DishRead]:
    """Получить список блюд, доступных в кафе."""
    dishes = await dish_crud.get_all(
        session=session,
        show_all=show_all,
        cafe_id=cafe_id,
    )

    return [build_dish_response(dish) for dish in dishes]


@router.post(
    '/',
    response_model=DishRead,
    status_code=status.HTTP_201_CREATED,
    summary='Создать новое блюдо',
)
async def create_dish(
    dish_in: DishCreate,
    session: AsyncSession = Depends(get_async_session),
    _: User = Depends(is_manager_or_admin), # Требуется роль Админ/Менеджер
) -> DishRead:
    """Создать новое блюдо в системе."""
    try:
        dish = await dish_crud.create(obj_in=dish_in, session=session)
        return build_dish_response(dish)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get('/{dish_id}', response_model=DishRead)
async def get_dish(
    dish_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    _: User = Depends(get_current_active_user),
) -> DishRead:
    """Получить блюдо по идентификатору."""
    dish = await _get_dish_or_404(dish_id, session)
    if not dish.is_active:
         is_admin_or_manager = (_.role in (UserRole.MANAGER, UserRole.ADMIN))
         if not is_admin_or_manager:
             raise HTTPException(status.HTTP_404_NOT_FOUND, 'Блюдо не найдено')

    return build_dish_response(dish)


@router.patch(
    '/{dish_id}',
    response_model=DishRead,
)
async def update_dish(
    dish_id: UUID,
    update_data: DishUpdate,
    session: AsyncSession = Depends(get_async_session),
    _: User = Depends(is_manager_or_admin),
) -> DishRead:
    """Изменение деталей блюда."""
    dish = await _get_dish_or_404(dish_id, session)
    updated_dish = await dish_crud.update(
        db_obj=dish,
        obj_in=update_data,
        session=session,
    )
    return build_dish_response(updated_dish)
