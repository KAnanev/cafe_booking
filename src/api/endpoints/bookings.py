from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.bookings import BookingAccess, get_booking_access
from core.db import get_async_session
from managers.booking_manager import BookingManager
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
    access: BookingAccess = Depends(get_booking_access),
) -> list[BookingInfo]:
    """Получить список бронирований."""
    manager = BookingManager(session)
    return await manager.list_bookings(
        show_all=show_all,
        cafe_id=cafe_id,
        user_id=user_id,
        allowed_user_id=access.user_id,
        allowed_cafe_ids=access.cafe_ids,
    )


@router.post(
    '/',
    response_model=BookingInfo,
    status_code=status.HTTP_201_CREATED,
)
async def create_booking(
    booking_in: BookingCreate,
    session: AsyncSession = Depends(get_async_session),
    access: BookingAccess = Depends(get_booking_access),
) -> BookingInfo:
    """Создать бронирование стола."""
    manager = BookingManager(session)
    return await manager.create_booking(
        booking_in,
        user_id=access.current_user.id,
        allowed_cafe_ids=access.cafe_ids,
    )


@router.get('/{booking_id}', response_model=BookingInfo)
async def get_booking(
    booking_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    access: BookingAccess = Depends(get_booking_access),
) -> BookingInfo:
    """Получить бронирование по идентификатору."""
    manager = BookingManager(session)
    return await manager.get_booking(
        booking_id,
        allowed_user_id=access.user_id,
        allowed_cafe_ids=access.cafe_ids,
    )
