from datetime import date as date_type
from datetime import datetime, timezone
from typing import Iterable, Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from crud.base import CRUDBase
from models.booking import Booking, BookingStatus
from models.booking_table_slot import BookingTableSlot
from models.cafe import Cafe
from models.relations import cafe_managers
from models.slots import Slot
from models.table import Table
from schemas.booking import BookingCreate, TablesSlots

_BUSY_STATUSES = (BookingStatus.BOOKING.value, BookingStatus.ACTIVE.value)


class BookingCRUD(CRUDBase[Booking, BookingCreate, BookingCreate]):
    """CRUD с валидацией для бронирований."""

    async def get_manager_cafe_ids(
        self,
        manager_id: UUID,
        session: AsyncSession,
    ) -> list[UUID]:
        """Возвращает список кафе менеджера."""
        query = select(cafe_managers.c.cafe_id).where(
            cafe_managers.c.user_id == manager_id,
        )
        result = await session.execute(query)
        return list(result.scalars().all())

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

    async def get_list(
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

    async def create(
        self,
        obj_in: BookingCreate,
        session: AsyncSession,
        user_id: UUID | None = None,
    ) -> Booking:
        """Создание бронирования с проверками."""
        await self._validate_booking_date(obj_in.booking_date)
        cafe = await self._get_cafe(obj_in.cafe_id, session)
        await self._validate_tables_slots(
            obj_in.tables_slots,
            cafe.id,
            session,
        )
        await self._ensure_slots_free(
            obj_in.tables_slots,
            obj_in.booking_date,
            session,
        )

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

    async def _validate_booking_date(self, booking_date: date_type) -> None:
        """Проверяет, что дата бронирования не в прошлом."""
        today = datetime.now(timezone.utc).date()
        if booking_date < today:
            msg = 'Нельзя забронировать дату в прошлом.'
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=msg)

    async def _get_cafe(self, cafe_id: UUID, session: AsyncSession) -> Cafe:
        """Проверяет наличие кафе."""
        cafe = await session.get(Cafe, cafe_id)
        if cafe is None or not cafe.is_active:
            msg = 'Кафе не найдено или не активно.'
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail=msg)
        return cafe

    async def _validate_tables_slots(
        self,
        tables_slots: Sequence[TablesSlots],
        cafe_id: UUID,
        session: AsyncSession,
    ) -> None:
        """Проверяет принадлежность столов и слотов кафе."""
        for pair in tables_slots:
            table = await session.get(Table, pair.table_id)
            if (
                table is None
                or not table.is_active
                or table.cafe_id != cafe_id
            ):
                msg = 'Стол не найден или не относится к кафе.'
                raise HTTPException(status.HTTP_404_NOT_FOUND, detail=msg)

            slot = await session.get(Slot, pair.slot_id)
            if slot is None or not slot.is_active or slot.cafe_id != cafe_id:
                msg = 'Слот не найден или не относится к кафе.'
                raise HTTPException(status.HTTP_404_NOT_FOUND, detail=msg)

    async def _ensure_slots_free(
        self,
        tables_slots: Iterable[TablesSlots],
        booking_date: date_type,
        session: AsyncSession,
    ) -> None:
        """Убедиться в отсутствии пересечений по столу/слоту/дате."""
        for pair in tables_slots:
            query = (
                select(BookingTableSlot.id)
                .join(Booking)
                .where(
                    and_(
                        BookingTableSlot.table_id == pair.table_id,
                        BookingTableSlot.slot_id == pair.slot_id,
                        Booking.booking_date == booking_date,
                        Booking.status.in_(_BUSY_STATUSES),
                        Booking.is_active.is_(True),
                    ),
                )
            )
            conflict = await session.execute(query)
            if conflict.scalars().first():
                msg = 'Слот стола уже занят на выбранную дату.'
                raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=msg)

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
