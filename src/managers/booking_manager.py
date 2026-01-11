from datetime import date, datetime, time, timedelta, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from core.constants import REMIND_MINUTES_BEFORE
from crud.booking import booking_crud
from crud.cafe import cafe_crud
from crud.slots import slot_crud
from crud.table import table_crud
from managers.exceptions import (
    BookingNotFound,
    BookingValidationError,
    PermissionDenied,
)
from managers.outbox_manager import OutboxManager, utcnow
from models.booking import Booking
from models.user import User, UserRole
from schemas.booking import (
    BookingCreate,
    BookingInfo,
    TablesSlots,
    TablesSlotsInfo,
)
from schemas.cafe import CafeReadShort
from schemas.slot import TimeSlotShort
from schemas.table import TableShort


class BookingManager:
    """Менеджер бронирований."""

    def __init__(self, session: AsyncSession) -> None:
        """Инициализирует менеджер сессией базы данных."""
        self.session = session

    async def _validate_booking_date(self, booking_date: date) -> None:
        if booking_date < date.today():
            raise BookingValidationError(
                'Нельзя бронировать на прошедшие даты.',
            )

    async def _validate_cafe(self, cafe_id: UUID) -> None:
        cafe = await cafe_crud.get_by_id(obj_id=cafe_id, session=self.session)
        if cafe is None or not cafe.is_active:
            raise BookingNotFound('Кафе не найдено или неактивно.')

    async def _validate_tables_slots(
        self,
        tables_slots: list[TablesSlots],
        cafe_id: UUID,
    ) -> None:
        for pair in tables_slots:
            table = await table_crud.get_by_id(
                obj_id=pair.table_id,
                session=self.session,
            )
            if table is None or not table.is_active:
                raise BookingNotFound('Стол не найден или неактивен.')
            if table.cafe_id != cafe_id:
                raise BookingValidationError(
                    'Стол не относится к выбранному кафе.',
                )

            slot = await slot_crud.get_by_id(
                obj_id=pair.slot_id,
                session=self.session,
            )
            if slot is None or not slot.is_active:
                raise BookingNotFound('Слот не найден или неактивен.')
            if slot.cafe_id != cafe_id:
                raise BookingValidationError(
                    'Слот не относится к выбранному кафе.',
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
                    'Стол уже забронирован на этот слот.',
                )

    async def _get_manager_cafe_ids(self, manager_id: UUID) -> list[UUID]:
        cafes = await cafe_crud.get_managed_cafes(
            session=self.session,
            user_id=manager_id,
        )
        return [cafe.id for cafe in cafes]

    async def _enqueue_booking_events_created(
        self,
        *,
        booking_id: UUID,
        user_id: UUID,
        cafe_id: UUID,
        booking_date: date,
        slot_start_time: time,
    ) -> None:
        """Собирает сообщение админам и пользователю."""
        outbox = OutboxManager(self.session)

        await outbox.add(
            event_type='booking.notify.admin.created',
            aggregate_type='booking',
            aggregate_id=booking_id,
            payload={
                'booking_id': str(booking_id),
                'user_id': str(user_id),
                'cafe_id': str(cafe_id),
                'booking_date': str(booking_date),
                'slot_start_time': slot_start_time.isoformat(),
            },
            available_at=utcnow(),
        )

        start_dt = datetime.combine(
            booking_date,
            slot_start_time,
            tzinfo=timezone.utc,
        )
        remind_at = start_dt - timedelta(minutes=REMIND_MINUTES_BEFORE)

        if remind_at <= utcnow():
            remind_at = utcnow()

        await outbox.add(
            event_type='booking.reminder.user',
            aggregate_type='booking',
            aggregate_id=booking_id,
            payload={
                'booking_id': str(booking_id),
                'user_id': str(user_id),
                'cafe_id': str(cafe_id),
                'booking_date': str(booking_date),
                'slot_start_time': slot_start_time.isoformat(),
                'remind_minutes_before': REMIND_MINUTES_BEFORE,
                'remind_at': remind_at.isoformat(),
            },
            available_at=remind_at,
        )

    async def list_bookings(
        self,
        show_all: bool = False,
        cafe_id: UUID | None = None,
        user_id: UUID | None = None,
        current_user: User | None = None,
    ) -> list[BookingInfo]:
        """Список бронирований."""
        if current_user is None:
            raise PermissionDenied('Нет доступа.')
        if current_user.role == UserRole.ADMIN:
            bookings = await booking_crud.get_list_all(
                session=self.session,
                show_all=show_all,
                cafe_id=cafe_id,
                user_id=user_id,
            )
            return [self._build_booking_info(booking) for booking in bookings]
        if current_user.role == UserRole.MANAGER:
            cafe_ids = await self._get_manager_cafe_ids(current_user.id)
            if not cafe_ids:
                return []
            if cafe_id and cafe_id not in cafe_ids:
                raise PermissionDenied('Нет доступа.')
            bookings = await booking_crud.get_list_all(
                session=self.session,
                show_all=show_all,
                cafe_id=cafe_id,
                cafe_ids=cafe_ids,
                user_id=user_id,
            )
            return [self._build_booking_info(booking) for booking in bookings]
        if user_id and user_id != current_user.id:
            raise PermissionDenied('Нет доступа.')
        bookings = await booking_crud.get_list_all(
            session=self.session,
            show_all=show_all,
            cafe_id=cafe_id,
            user_id=current_user.id,
        )
        return [self._build_booking_info(booking) for booking in bookings]

    async def get_booking(
        self,
        booking_id: UUID,
        current_user: User | None = None,
    ) -> BookingInfo:
        """Получить бронирование по id."""
        booking = await booking_crud.get_by_id_with_relations(
            booking_id=booking_id,
            session=self.session,
        )
        if booking is None:
            raise BookingNotFound('Бронирование не найдено.')
        if current_user is None:
            raise PermissionDenied('Нет доступа.')
        if current_user.role == UserRole.ADMIN:
            return self._build_booking_info(booking)
        if current_user.role == UserRole.MANAGER:
            cafe_ids = await self._get_manager_cafe_ids(current_user.id)
            if booking.cafe_id not in cafe_ids:
                raise PermissionDenied('Нет доступа.')
            return self._build_booking_info(booking)
        if booking.user_id != current_user.id:
            raise PermissionDenied('Нет доступа.')
        return self._build_booking_info(booking)

    async def create_booking(
        self,
        booking_in: BookingCreate,
        current_user: User | None = None,
    ) -> BookingInfo:
        """Создать бронирование."""
        if current_user is None:
            raise PermissionDenied('Нет доступа.')
        if current_user.role == UserRole.MANAGER:
            cafe_ids = await self._get_manager_cafe_ids(current_user.id)
            if not cafe_ids or booking_in.cafe_id not in cafe_ids:
                raise PermissionDenied('Нет доступа.')
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
            user_id=current_user.id,
        )
        booking = await booking_crud.get_by_id_with_relations(
            booking_id=booking.id,
            session=self.session,
            show_all=True,
        )
        if booking is None:
            raise BookingNotFound('Бронирование не найдено.')

        slot_ids = [p.slot_id for p in booking_in.tables_slots]
        slot_start_time = await slot_crud.get_min_start_time(
            session=self.session,
            cafe_id=booking_in.cafe_id,
            slot_ids=slot_ids,
        )

        await self._enqueue_booking_events_created(
            booking_id=booking.id,
            user_id=current_user.id,
            cafe_id=booking_in.cafe_id,
            booking_date=booking_in.booking_date,
            slot_start_time=slot_start_time,
        )

        return self._build_booking_info(booking)

    def _build_booking_info(self, booking: Booking) -> BookingInfo:
        """Формирует ответ по бронированию."""
        cafe_short = CafeReadShort.model_validate(
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
