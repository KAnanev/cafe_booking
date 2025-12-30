from fastapi import Depends, HTTPException, status

from api.dependencies.auth import get_optional_user


async def get_current_active_user(user=Depends(get_optional_user)):
    """Dependency that returns the current authenticated user or raises 401."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not authenticated',
        )
    return user

