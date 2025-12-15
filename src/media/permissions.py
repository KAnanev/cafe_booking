# src/media/permissions.py
from fastapi import Depends, HTTPException, status

from src.core.security import get_current_user
from src.users.models import User


ALLOWED_ROLES = {"admin", "manager"}


def can_upload_image(
    user: User = Depends(get_current_user),
) -> User:
    if user.role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to upload image",
        )
    return user
