import logging

from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from crud.user import user_crud
from managers.user_manager import UserManager
from schemas.user import UserCreate

logger = logging.getLogger('uvicorn.error')


async def create_first_superuser(session: AsyncSession) -> None:
    """Создает суперпользователя."""
    if not settings.first_superuser_email:
        logger.info(
            'FIRST_SUPERUSER_EMAIL не задан —'
            'создание суперпользователя пропущено',
        )
        return

    logger.info(
        'Проверка существования суперпользователя: %s',
        settings.first_superuser_email,
    )

    existing_user = await user_crud.get_by_email(
        email=settings.first_superuser_email,
        session=session,
    )

    if existing_user:
        logger.info(
            'Суперпользователь уже существует: %s',
            existing_user.email,
        )
        return

    logger.warning(
        'Суперпользователь не найден — будет создан: %s',
        settings.first_superuser_email,
    )

    user = UserCreate(
        username=settings.first_superuser_email,
        email=settings.first_superuser_email,
        password=settings.first_superuser_password,
    )

    manager = UserManager(session)

    try:
        user = await manager.create_superuser(user)
    except Exception:
        logger.exception(
            'Ошибка при создании суперпользователя: %s',
            settings.first_superuser_email,
        )
        raise

    print(user)

    logger.info(
        'Суперпользователь успешно создан: %s',
        settings.first_superuser_email,
    )
