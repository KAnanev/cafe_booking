from fastapi import FastAPI

from src.api.routers import main_router
from src.core.config import settings
from src.core.init_db import create_first_superuser


async def lifespan(app):
    await create_first_superuser()
    yield


app = FastAPI(
    title=settings.app_title,
    description=settings.app_desc,
    lifespan=lifespan,
)

app.include_router(main_router)
