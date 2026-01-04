from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from crud.cafe import cafe_crud
from crud.slots import slot_crud
from managers.exceptions import (
    PermissionDenied,
    SlotNotFound,
    SlotValidationError,
)
from models.slots import Slot
from models.user import User, UserRole
from schemas.slot import SlotCreate, SlotUpdate


class SlotManager:
    """Менеджер слотов: бизнес-логика и оркестрация операций со слотами."""

    def __init__(self, session: AsyncSession) -> None:
        """Инициализирует менеджер слотов."""
        self.session = session

    async def _get_manager_cafe_ids(self, manager_id: UUID) -> list[UUID]:
        cafes = await cafe_crud.get_managed_cafes(
            session=self.session,
            user_id=manager_id,
        )
        return [cafe.id for cafe in cafes]

    async def _ensure_can_manage_cafe(self, cafe_id: UUID, user: User) -> None:
        if user.role == UserRole.ADMIN:
            return
        if user.role == UserRole.MANAGER:
            cafe_ids = await self._get_manager_cafe_ids(user.id)
            if cafe_id in cafe_ids:
                return
        raise PermissionDenied('Нет доступа.')

    async def list_slots(self, cafe_id: UUID, show_all: bool) -> list[Slot]:
        """Возвращает список слотов указанного кафе."""
        slots = await slot_crud.get_by_cafe(
            session=self.session,
            cafe_id=cafe_id,
            show_all=show_all,
        )
        return list(slots)

    async def create_slot(
        self,
        cafe_id: UUID,
        slot_in: SlotCreate,
        current_user: User,
    ) -> Slot:
        """Создаёт слот в указанном кафе."""
        await self._ensure_can_manage_cafe(cafe_id=cafe_id, user=current_user)

        if (
            getattr(slot_in, 'cafe_id', None) is not None
            and slot_in.cafe_id != cafe_id
        ):
            raise SlotValidationError(
                'cafe_id в теле не совпадает с cafe_id в пути',
            )

        slot_in = slot_in.model_copy(update={"cafe_id": cafe_id})

        exists = await slot_crud.exists_slot(
            session=self.session,
            cafe_id=cafe_id,
            start=slot_in.start_time,
            end=slot_in.end_time,
        )
        if exists:
            raise SlotValidationError('Слот с таким временем уже существует')

        try:
            return await slot_crud.create(obj_in=slot_in, session=self.session)
        except ValueError as exc:
            raise SlotValidationError(str(exc)) from exc

    async def update_slot(
        self,
        cafe_id: UUID,
        slot_id: UUID,
        slot_in: SlotUpdate,
        current_user: User,
    ) -> Slot:
        """Обновляет слот в рамках указанного кафе."""
        await self._ensure_can_manage_cafe(cafe_id=cafe_id, user=current_user)

        slot = await slot_crud.get_by_cafe_and_id(
            session=self.session,
            cafe_id=cafe_id,
            slot_id=slot_id,
            show_all=True,
        )
        if slot is None:
            raise SlotNotFound('Слот не найден.')

        if slot_in.cafe_id is not None and slot_in.cafe_id != cafe_id:
            raise SlotValidationError(
                'cafe_id в теле не совпадает с cafe_id в пути',
            )

        update_data = slot_in.model_dump(
            exclude_unset=True,
            exclude={"cafe_id"},
        )

        start = update_data.get('start_time', slot.start_time)
        end = update_data.get('end_time', slot.end_time)
        exists = await slot_crud.exists_slot(
            session=self.session,
            cafe_id=cafe_id,
            start=start,
            end=end,
            exclude_id=slot.id,
        )
        if exists:
            raise SlotValidationError('Слот с таким временем уже существует')

        try:
            return await slot_crud.update(
                db_obj=slot,
                obj_in=update_data,
                session=self.session,
            )
        except ValueError as exc:
            raise SlotValidationError(str(exc)) from exc
