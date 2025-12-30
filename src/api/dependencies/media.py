from fastapi import Depends, HTTPException, status

from api.dependencies.auth import get_optional_user
from models.user import User, UserRole


async def can_upload_image(
    user: User | None = Depends(get_optional_user),
) -> User:
    """Разрешает загрузку изображений только менеджерам и админам."""
    if not user or user.role not in (UserRole.MANAGER, UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Не достаточно прав для загрузки изображения.',
        )
    return user
