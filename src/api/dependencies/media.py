from fastapi import Depends

from api.dependencies.auth import require_admin_or_manager
from models.user import User


async def can_upload_image(
    user: User = Depends(require_admin_or_manager),
) -> User:
    """Разрешает загрузку изображений только менеджерам и админам."""
    return user
