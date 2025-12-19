from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.users import get_current_active_user
from core.db import get_async_session
from managers.booking_manager import BookingManager
from models.user import User
from schemas.booking import BookingCreate, BookingInfo

router = APIRouter()


@router.get('/', response_model=list[BookingInfo])
async def list_bookings(
    show_all: bool = Query(False, description='Показывать все бронирования?'),
    cafe_id: UUID | None = Query(
        None,
        description='ID кафе для фильтрации бронирований.',
    ),
    user_id: UUID | None = Query(
        None,
        description='ID пользователя для фильтрации бронирований.',
    ),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user),
) -> list[BookingInfo]:
    """Получить список бронирований."""
    manager = BookingManager(session)
    return await manager.list_bookings(
        current_user=current_user,
        show_all=show_all,
        cafe_id=cafe_id,
        user_id=user_id,
    )


@router.post(
    '/',
    response_model=BookingInfo,
    status_code=status.HTTP_201_CREATED,
)
async def create_booking(
    booking_in: BookingCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user),
) -> BookingInfo:
    """Создать бронирование стола."""
    manager = BookingManager(session)
    return await manager.create_booking(booking_in, current_user)


@router.get('/{booking_id}', response_model=BookingInfo)
async def get_booking(
    booking_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user),
) -> BookingInfo:
    """Получить бронирование по идентификатору."""
    manager = BookingManager(session)
    return await manager.get_booking(booking_id, current_user)
