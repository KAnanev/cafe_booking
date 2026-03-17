from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from api.dependencies.managers import get_slot_manager
from auth.domain.permissions.presets import require_admin_or_manager
from managers.slot_manager import SlotManager
from models.cafe import Cafe
from models.user import User
from schemas.slot import SlotCreate, SlotRead, SlotUpdate
from validators.cafes import get_cafe_or_404

router = APIRouter()


@router.get(
    '',
    response_model=list[SlotRead],
    summary='Получить слоты кафе',
)
async def get_slots(
    show_all: bool = Query(False, description='Показывать неактивные слоты'),
    cafe: Cafe = Depends(get_cafe_or_404),
    slot_manager: SlotManager = Depends(get_slot_manager),
) -> list[SlotRead]:
    """Получить список временных слотов для указанного кафе."""
    slots = await slot_manager.list_slots(
        cafe_id=cafe.id,
        show_all=show_all,
    )
    return [SlotRead.model_validate(slot) for slot in slots]


@router.post(
    '',
    response_model=SlotRead,
    status_code=status.HTTP_201_CREATED,
    summary='Создать слот',
)
async def create_slot(
    slot_in: SlotCreate,
    cafe: Cafe = Depends(get_cafe_or_404),
    current_user: User = Depends(require_admin_or_manager),
    slot_manager: SlotManager = Depends(get_slot_manager),
) -> SlotRead:
    """Создать новый временной слот для указанного кафе."""
    slot = await slot_manager.create_slot(
        cafe_id=cafe.id,
        slot_in=slot_in,
        current_user=current_user,
    )
    return SlotRead.model_validate(slot)


@router.patch(
    '/{slot_id}',
    response_model=SlotRead,
    summary='Обновить слот',
)
async def update_slot(
    slot_id: UUID,
    slot_in: SlotUpdate,
    cafe: Cafe = Depends(get_cafe_or_404),
    current_user: User = Depends(require_admin_or_manager),
    slot_manager: SlotManager = Depends(get_slot_manager),
) -> SlotRead:
    """Обновить данные слота."""
    slot = await slot_manager.update_slot(
        cafe_id=cafe.id,
        slot_id=slot_id,
        slot_in=slot_in,
        current_user=current_user,
    )
    return SlotRead.model_validate(slot)
