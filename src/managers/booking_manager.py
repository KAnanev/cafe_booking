from datetime import date
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from crud.booking import booking_crud
from managers.exceptions import (
    BookingNotFound,
    BookingValidationError,
    PermissionDenied,
)
from models.booking import Booking
from schemas.booking import (
    BookingCreate,
    BookingInfo,
    TablesSlots,
    TablesSlotsInfo,
)
from schemas.cafe import CafeShort
from schemas.slot import TimeSlotShort
from schemas.table import TableShort


class BookingManager:
    """Менеджер бронирований."""

    def __init__(self, session: AsyncSession) -> None:
        """Инициализирует менеджер сессией базы данных."""
        self.session = session

    async def _validate_booking_date(self, booking_date: date) -> None:
        if booking_date < date.today():
            raise BookingValidationError('Booking date cannot be in the past.')

    async def _validate_cafe(self, cafe_id: UUID) -> None:
        cafe = await booking_crud.get_cafe_by_id(
            cafe_id=cafe_id,
            session=self.session,
        )
        if cafe is None or not cafe.is_active:
            raise BookingNotFound('Cafe not found or inactive.')

    async def _validate_tables_slots(
        self,
        tables_slots: list[TablesSlots],
        cafe_id: UUID,
    ) -> None:
        for pair in tables_slots:
            table = await booking_crud.get_table_by_id(
                table_id=pair.table_id,
                session=self.session,
            )
            if table is None or not table.is_active:
                raise BookingNotFound('Table not found or inactive.')
            if table.cafe_id != cafe_id:
                raise BookingValidationError(
                    'Table does not belong to the selected cafe.',
                )

            slot = await booking_crud.get_slot_by_id(
                slot_id=pair.slot_id,
                session=self.session,
            )
            if slot is None or not slot.is_active:
                raise BookingNotFound('Slot not found or inactive.')
            if slot.cafe_id != cafe_id:
                raise BookingValidationError(
                    'Slot does not belong to the selected cafe.',
                )

    async def _ensure_slots_free(
        self,
        tables_slots: list[TablesSlots],
        booking_date: date,
    ) -> None:
        for pair in tables_slots:
            is_taken = await booking_crud.is_slot_taken(
                table_id=pair.table_id,
                slot_id=pair.slot_id,
                booking_date=booking_date,
                session=self.session,
            )
            if is_taken:
                raise BookingValidationError(
                    'Selected table is already booked for this slot.',
                )

    async def list_bookings(
        self,
        show_all: bool = False,
        cafe_id: UUID | None = None,
        user_id: UUID | None = None,
        allowed_user_id: UUID | None = None,
        allowed_cafe_ids: list[UUID] | None = None,
    ) -> list[BookingInfo]:
        """Возвращает список бронирований."""
        if allowed_cafe_ids is not None:
            if not allowed_cafe_ids:
                return []
            if cafe_id and cafe_id not in allowed_cafe_ids:
                raise PermissionDenied('Нет доступа к этому кафе')
        if allowed_user_id is not None:
            if user_id and user_id != allowed_user_id:
                raise PermissionDenied('Нет доступа к чужим бронированиям')
            user_id = allowed_user_id
        bookings = await booking_crud.get_list(
            session=self.session,
            show_all=show_all,
            cafe_id=cafe_id,
            cafe_ids=allowed_cafe_ids,
            user_id=user_id,
        )
        return [self._build_booking_info(booking) for booking in bookings]

    async def get_booking(
        self,
        booking_id: UUID,
        allowed_user_id: UUID | None = None,
        allowed_cafe_ids: list[UUID] | None = None,
    ) -> BookingInfo:
        """Возвращает бронирование по идентификатору."""
        booking = await booking_crud.get_by_id_with_relations(
            booking_id=booking_id,
            session=self.session,
        )
        if booking is None:
            raise BookingNotFound('Бронь не найдена.')
        if allowed_cafe_ids is not None:
            if not allowed_cafe_ids:
                raise PermissionDenied('Нет доступа к этому бронированию')
            if booking.cafe_id not in allowed_cafe_ids:
                raise PermissionDenied('Нет доступа к этому бронированию')
        if allowed_user_id is not None and booking.user_id != allowed_user_id:
            raise PermissionDenied('Нет доступа к чужим бронированиям')
        return self._build_booking_info(booking)

    async def create_booking(
        self,
        booking_in: BookingCreate,
        user_id: UUID,
        allowed_cafe_ids: list[UUID] | None = None,
    ) -> BookingInfo:
        """Создаёт бронирование."""
        if allowed_cafe_ids is not None:
            if not allowed_cafe_ids:
                raise PermissionDenied('Нет доступа к этому кафе')
            if booking_in.cafe_id not in allowed_cafe_ids:
                raise PermissionDenied('Нет доступа к этому кафе')
        await self._validate_booking_date(booking_in.booking_date)
        await self._validate_cafe(booking_in.cafe_id)
        await self._validate_tables_slots(
            booking_in.tables_slots,
            booking_in.cafe_id,
        )
        await self._ensure_slots_free(
            booking_in.tables_slots,
            booking_in.booking_date,
        )
        booking = await booking_crud.create(
            obj_in=booking_in,
            session=self.session,
            user_id=user_id,
        )
        booking = await booking_crud.get_by_id_with_relations(
            booking_id=booking.id,
            session=self.session,
            show_all=True,
        )
        if booking is None:
            raise BookingNotFound('Бронь не найдена.')
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
