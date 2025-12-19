from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from crud.booking import booking_crud
from managers.exceptions import PermissionDenied
from models.booking import Booking
from models.user import User, UserRole
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
        current_user: User,
        show_all: bool = False,
        cafe_id: UUID | None = None,
        user_id: UUID | None = None,
    ) -> list[BookingInfo]:
        """Возвращает список бронирований."""
        cafe_ids: list[UUID] | None = None
        if current_user.role == UserRole.MANAGER:
            cafe_ids = await booking_crud.get_manager_cafe_ids(
                manager_id=current_user.id,
                session=self.session,
            )
            if not cafe_ids:
                return []
            if cafe_id and cafe_id not in cafe_ids:
                raise PermissionDenied('Нет доступа к этому кафе')
        if current_user.role == UserRole.USER:
            if user_id and user_id != current_user.id:
                raise PermissionDenied('Нет доступа к чужим бронированиям')
            user_id = current_user.id
        bookings = await booking_crud.get_list(
            session=self.session,
            show_all=show_all,
            cafe_id=cafe_id,
            cafe_ids=cafe_ids,
            user_id=user_id,
        )
        return [self._build_booking_info(booking) for booking in bookings]

    async def get_booking(
        self,
        booking_id: UUID,
        current_user: User,
    ) -> BookingInfo:
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
        await self._ensure_access(current_user, booking)
        return self._build_booking_info(booking)

    async def create_booking(
        self,
        booking_in: BookingCreate,
        current_user: User,
    ) -> BookingInfo:
        """Создаёт бронирование."""
        await self._ensure_create_access(current_user, booking_in.cafe_id)
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
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Бронь не найдена.',
            )
        return self._build_booking_info(booking)

    async def _ensure_create_access(
        self,
        current_user: User,
        cafe_id: UUID,
    ) -> None:
        """Проверяет доступ на создание бронирования."""
        if current_user.role == UserRole.MANAGER:
            cafe_ids = await booking_crud.get_manager_cafe_ids(
                manager_id=current_user.id,
                session=self.session,
            )
            if cafe_id not in cafe_ids:
                raise PermissionDenied('Нет доступа к этому кафе')

    async def _ensure_access(self, current_user: User, booking: Booking) -> None:
        """Проверяет доступ к бронированию."""
        if current_user.role == UserRole.ADMIN:
            return
        if current_user.role == UserRole.MANAGER:
            cafe_ids = await booking_crud.get_manager_cafe_ids(
                manager_id=current_user.id,
                session=self.session,
            )
            if booking.cafe_id not in cafe_ids:
                raise PermissionDenied('Нет доступа к этому бронированию')
            return
        if booking.user_id != current_user.id:
            raise PermissionDenied('Нет доступа к чужим бронированиям')

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
