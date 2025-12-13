from fastapi import FastAPI

from api.routers import main_router
from core.config import settings


async def lifespan(app: FastAPI) -> None:
    """Асинхронная функция жизненного цикла приложения FastAPI.

    Инициализирует данные при запуске приложения.
    """
    yield  # Указывает, что событие произошло


app = FastAPI(
    title=settings.app_title,
    description=settings.app_desc,
    lifespan=lifespan,
)

app.include_router(main_router)
