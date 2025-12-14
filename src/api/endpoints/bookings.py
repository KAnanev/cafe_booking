from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.utils import build_booking_info
from core.db import get_async_session
from crud.booking import booking_crud
from models.booking import Booking
from schemas.booking import BookingCreate, BookingInfo

router = APIRouter(prefix="/booking", tags=["Бронирования"])


async def _get_booking_or_404(
    booking_id: UUID,
    session: AsyncSession,
) -> Booking:
    booking = await session.get(Booking, booking_id)
    if booking is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Бронь не найдена.")
    return booking


def _build_booking_response(booking: Booking) -> BookingInfo:
    """Формирует ответ по бронированию согласно схеме."""
    return build_booking_info(booking)


@router.get("/", response_model=list[BookingInfo])
async def list_bookings(
    show_all: bool = Query(False, description="Показывать все бронирования?"),
    cafe_id: UUID | None = Query(
        None,
        description="ID кафе для фильтрации бронирований.",
    ),
    user_id: UUID | None = Query(
        None,
        description="ID пользователя для фильтрации бронирований.",
    ),
    session: AsyncSession = Depends(get_async_session),
) -> list[BookingInfo]:
    """Получить список бронирований."""
    query = select(Booking)
    if cafe_id:
        query = query.where(Booking.cafe_id == cafe_id)
    if user_id:
        query = query.where(Booking.user_id == user_id)
    if not show_all:
        query = query.where(Booking.is_active.is_(True))
    result = await session.execute(query)
    bookings = result.scalars().unique().all()
    for booking in bookings:
        _ = booking.tables_slots
    return [_build_booking_response(booking) for booking in bookings]


@router.post(
    "/",
    response_model=BookingInfo,
    status_code=status.HTTP_201_CREATED,
)
async def create_booking(
    booking_in: BookingCreate,
    session: AsyncSession = Depends(get_async_session),
) -> BookingInfo:
    """Создать бронирование стола."""
    booking = await booking_crud.create(booking_in, session)
    await session.refresh(booking)
    _ = booking.tables_slots
    return _build_booking_response(booking)


@router.get("/{booking_id}", response_model=BookingInfo)
async def get_booking(
    booking_id: UUID,
    session: AsyncSession = Depends(get_async_session),
) -> BookingInfo:
    """Получить бронирование по идентификатору."""
    booking = await _get_booking_or_404(booking_id, session)
    _ = booking.tables_slots
    return _build_booking_response(booking)
