from fastapi import Depends, HTTPException, status

from api.dependencies.users import get_current_active_user
from models.cafe import Cafe
from models.user import User, UserRole
from validators.cafes import get_cafe_or_404


async def is_manager_or_admin(
        user: User = Depends(get_current_active_user),
) -> User:
    """Разрешает доступ только менеджерам и администраторам."""
    if user.role not in (UserRole.MANAGER, UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Not enough permissions',
        )
    return user


async def can_manage_cafe(
    cafe: Cafe = Depends(get_cafe_or_404),
    user: User = Depends(get_current_active_user),
) -> User:
    """Разрешает доступ менеджерам своего кафе и администраторам."""
    if user.role == UserRole.ADMIN:
        return user

    if user.role == UserRole.MANAGER and user in cafe.managers:
        return user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail='Not enough permissions',
    )
