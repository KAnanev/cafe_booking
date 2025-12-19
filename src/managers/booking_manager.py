from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from crud.booking import booking_crud
from models.booking import Booking
from schemas.booking import BookingCreate, BookingInfo, TablesSlotsInfo
from schemas.cafe import CafeShort
from schemas.slot import TimeSlotShort
from schemas.table import TableShort


class BookingManager:
    """Менеджер бронирований."""

    def __init__(self, session: AsyncSession) -> None:
        """Инициализирует менеджер сессией базы данных."""
        self.session = session

    async def list_bookings(
        self,
        show_all: bool = False,
        cafe_id: UUID | None = None,
        user_id: UUID | None = None,
    ) -> list[BookingInfo]:
        """Возвращает список бронирований."""
        bookings = await booking_crud.get_list(
            session=self.session,
            show_all=show_all,
            cafe_id=cafe_id,
            user_id=user_id,
        )
        return [self._build_booking_info(booking) for booking in bookings]

    async def get_booking(self, booking_id: UUID) -> BookingInfo:
        """Возвращает бронирование по идентификатору."""
        booking = await booking_crud.get_by_id_with_relations(
            booking_id=booking_id,
            session=self.session,
        )
        if booking is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Бронь не найдена.',
            )
        return self._build_booking_info(booking)

    async def create_booking(self, booking_in: BookingCreate) -> BookingInfo:
        """Создаёт бронирование."""
        booking = await booking_crud.create(
            obj_in=booking_in,
            session=self.session,
        )
        booking = await booking_crud.get_by_id_with_relations(
            booking_id=booking.id,
            session=self.session,
            show_all=True,
        )
        if booking is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Бронь не найдена.',
            )
        return self._build_booking_info(booking)

    def _build_booking_info(self, booking: Booking) -> BookingInfo:
        """Формирует ответ по бронированию."""
        cafe_short = CafeShort.model_validate(
            booking.cafe,
            from_attributes=True,
        )
        tables_slots = []
        for link in booking.tables_slots:
            table_short = TableShort.model_validate(
                link.table,
                from_attributes=True,
            )
            slot_short = TimeSlotShort.model_validate(
                link.slot,
                from_attributes=True,
            )
            tables_slots.append(
                TablesSlotsInfo.model_validate(
                    {
                        **link.__dict__,
                        'table': table_short,
                        'slot': slot_short,
                    },
                    from_attributes=True,
                ),
            )
        return BookingInfo.model_validate(
            {
                **booking.__dict__,
                'user': None,
                'cafe': cafe_short,
                'tables_slots': tables_slots,
            },
            from_attributes=True,
        )
