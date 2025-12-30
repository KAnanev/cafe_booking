from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import FastAPI

from api.exception_handlers import register_exception_handlers
from api.media import router as media_router
from api.routers import main_router
from core.config import settings
from core.db import AsyncSessionLocal
from core.init_db import create_first_superuser
from core.logging import LoggingMiddleware, setup_logging

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    """Асинхронная функция жизненного цикла приложения FastAPI.

    Инициализирует данные при запуске приложения.
    """
    async with AsyncSessionLocal() as session:
        await create_first_superuser(session)
    yield


app = FastAPI(
    title=settings.app_title,
    description=settings.app_desc,
    openapi_tags=settings.openapi_tags,
    lifespan=lifespan,
)
register_exception_handlers(app)

app.add_middleware(LoggingMiddleware)

app.include_router(main_router)
app.include_router(media_router, prefix='/media', tags=['media'])
