from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from crud.user import user_crud
from managers.user_manager import UserManager
from models.user import UserRoles
from schemas.user import UserCreate


async def create_first_superuser(session: AsyncSession) -> None:
    """Создает суперпользователя."""
    if not settings.first_superuser_email:
        return

    existing_user = await user_crud.get_by_email(
        email=settings.first_superuser_email,
        session=session,
    )

    if existing_user:
        return

    user_in = UserCreate(
        username=settings.first_superuser_email,
        email=settings.first_superuser_email,
        password=settings.first_superuser_password,
        role=UserRoles.ADMIN,
    )

    manager = UserManager(session)
    await manager.create_superuser(user_in)
