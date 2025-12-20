from dataclasses import dataclass
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.users import get_current_active_user
from core.db import get_async_session
from crud.booking import booking_crud
from models.user import User, UserRole


@dataclass(slots=True)
class BookingAccess:
    """Контекст доступа к бронированиям."""

    user_id: UUID | None
    cafe_ids: list[UUID] | None
    current_user: User


async def get_booking_access(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user),
) -> BookingAccess:
    """Возвращает ограничения доступа к бронированиям."""
    if current_user.role == UserRole.ADMIN:
        return BookingAccess(
            user_id=None,
            cafe_ids=None,
            current_user=current_user,
        )
    if current_user.role == UserRole.MANAGER:
        cafe_ids = await booking_crud.get_manager_cafe_ids(
            manager_id=current_user.id,
            session=session,
        )
        return BookingAccess(
            user_id=None,
            cafe_ids=cafe_ids,
            current_user=current_user,
        )
    return BookingAccess(
        user_id=current_user.id,
        cafe_ids=None,
        current_user=current_user,
    )
