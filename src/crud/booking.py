from datetime import date as date_type
from typing import Sequence
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from crud.base import CRUDBase
from models.booking import Booking, BookingStatus
from models.booking_table_slot import BookingTableSlot
from schemas.booking import BookingCreate, TablesSlots

_BUSY_STATUSES = (BookingStatus.BOOKING.value, BookingStatus.ACTIVE.value)


class BookingCRUD(CRUDBase[Booking, BookingCreate, BookingCreate]):
    """CRUD с валидацией для бронирований."""

    async def get_by_id_with_relations(
        self,
        booking_id: UUID,
        session: AsyncSession,
        show_all: bool = True,
    ) -> Booking | None:
        """Получает бронирование с зависимостями."""
        query = (
            select(Booking)
            .options(
                selectinload(Booking.cafe),
                selectinload(Booking.tables_slots).selectinload(
                    BookingTableSlot.table,
                ),
                selectinload(Booking.tables_slots).selectinload(
                    BookingTableSlot.slot,
                ),
            )
            .where(Booking.id == booking_id)
        )
        if not show_all:
            query = query.where(Booking.is_active.is_(True))
        result = await session.execute(query)
        return result.scalars().first()

    async def get_list_all(
        self,
        session: AsyncSession,
        show_all: bool = False,
        cafe_id: UUID | None = None,
        cafe_ids: Sequence[UUID] | None = None,
        user_id: UUID | None = None,
    ) -> list[Booking]:
        """Получает список бронирований с зависимостями."""
        query = select(Booking).options(
            selectinload(Booking.cafe),
            selectinload(Booking.tables_slots).selectinload(
                BookingTableSlot.table,
            ),
            selectinload(Booking.tables_slots).selectinload(
                BookingTableSlot.slot,
            ),
        )
        if cafe_ids:
            query = query.where(Booking.cafe_id.in_(cafe_ids))
        elif cafe_id:
            query = query.where(Booking.cafe_id == cafe_id)
        if user_id:
            query = query.where(Booking.user_id == user_id)
        if not show_all:
            query = query.where(Booking.is_active.is_(True))
        result = await session.execute(query)
        return result.scalars().unique().all()

    async def get_list_by_user(
        self,
        session: AsyncSession,
        user_id: UUID,
        show_all: bool = False,
        cafe_id: UUID | None = None,
    ) -> list[Booking]:
        """Получает список бронирований пользователя с зависимостями."""
        return await self.get_list_all(
            session=session,
            show_all=show_all,
            cafe_id=cafe_id,
            user_id=user_id,
        )

    async def is_slot_taken(
        self,
        table_id: UUID,
        slot_id: UUID,
        booking_date: date_type,
        session: AsyncSession,
    ) -> bool:
        """Проверяет занятость слота на дату."""
        query = (
            select(BookingTableSlot.id)
            .join(Booking)
            .where(
                and_(
                    BookingTableSlot.table_id == table_id,
                    BookingTableSlot.slot_id == slot_id,
                    Booking.booking_date == booking_date,
                    Booking.status.in_(_BUSY_STATUSES),
                    Booking.is_active.is_(True),
                ),
            )
        )
        conflict = await session.execute(query)
        return conflict.scalars().first() is not None

    async def create(
        self,
        obj_in: BookingCreate,
        session: AsyncSession,
        user_id: UUID | None = None,
    ) -> Booking:
        """Создание бронирования."""
        booking = Booking(
            user_id=user_id,
            cafe_id=obj_in.cafe_id,
            guest_number=obj_in.guest_number,
            note=obj_in.note,
            status=obj_in.status.value,
            booking_date=obj_in.booking_date,
        )
        session.add(booking)
        await session.flush()

        await self._save_tables_slots(
            booking=booking,
            tables_slots=obj_in.tables_slots,
            session=session,
        )
        await session.commit()
        await session.refresh(booking)
        return booking

    async def _save_tables_slots(
        self,
        booking: Booking,
        tables_slots: Sequence[TablesSlots],
        session: AsyncSession,
    ) -> None:
        """Создает записи связок стол/слот."""
        for pair in tables_slots:
            link = BookingTableSlot(
                booking_id=booking.id,
                table_id=pair.table_id,
                slot_id=pair.slot_id,
            )
            session.add(link)


booking_crud = BookingCRUD(Booking)
