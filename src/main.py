from fastapi import FastAPI

from api.routers import main_router
from core.config import settings
from core.init_db import create_first_superuser


async def lifespan(app: FastAPI) -> None:
    """Асинхронная функция жизненного цикла приложения FastAPI.

    Инициализирует данные при запуске приложения.
    """
    await create_first_superuser()
    yield  # Указывает, что событие произошло


app = FastAPI(
    title=settings.app_title,
    description=settings.app_desc,
    lifespan=lifespan,
)

app.include_router(main_router)
