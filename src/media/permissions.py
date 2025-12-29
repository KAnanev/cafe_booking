# src/media/permissions.py
from fastapi import Depends, HTTPException, status

from api.dependencies.users import get_current_user
from models.user import Roles, User


async def can_upload_image(
    user: User = Depends(get_current_user),
) -> User:
    """Разрешает загрузку изображений только менеджерам и админам."""
    if user.role not in (Roles.MANAGER, Roles.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Не достаточно прав для загрузки изображения.",
        )
    return user
