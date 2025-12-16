from fastapi import FastAPI

from api.routers import main_router
from core.config import settings
from core.logging import LoggingMiddleware, setup_logging

setup_logging()

app = FastAPI(
    title=settings.app_title,
    description=settings.app_desc,
)

app.add_middleware(LoggingMiddleware)

app.include_router(main_router)
