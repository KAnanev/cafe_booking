# src/media/permissions.py
from fastapi import Depends, HTTPException, status

from api.dependencies.users import get_current_user
from models.user import Roles, User


async def can_upload_image(
    user: User = Depends(get_current_user),
) -> User:
    """Allow only managers and admins to upload images."""
    if user.role not in (Roles.MANAGER, Roles.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to upload image",
        )
    return user
