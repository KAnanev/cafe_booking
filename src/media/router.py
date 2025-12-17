from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_async_session
from media.permissions import can_upload_image
from media.schemas import ImageUploadResponse
from media.service import get_image, upload_image
from models.user import User

router = APIRouter()


@router.post(
    "",
    response_model=ImageUploadResponse,
    status_code=201,
)
async def upload_image_endpoint(
    file: UploadFile = File(...),
    user: User = Depends(can_upload_image),
    db: AsyncSession = Depends(get_async_session),
) -> dict[str, any]:
    """Загружает изображение и возвращает его ID."""
    image_id = await upload_image(
        db=db,
        file=file,
        username=user.username,
    )
    return {"id": image_id}


@router.get(
    "/{image_id}",
    responses={200: {"content": {"image/jpeg": {}}}},
)
async def get_image_endpoint(
    image_id: UUID,
    db: AsyncSession = Depends(get_async_session),
) -> FileResponse:
    """Возвращает эндпоинт для изображения по его UUID."""
    return await get_image(db=db, image_id=image_id)
