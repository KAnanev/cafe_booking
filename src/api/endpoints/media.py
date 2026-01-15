from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.media import can_upload_image
from core.db import get_async_session
from models.user import User
from schemas.media import ImageUploadResponse
from services.media import get_image, upload_image

router = APIRouter()


@router.post(
    '',
    response_model=ImageUploadResponse,
    status_code=201,
    summary="Загрузить изображение",
)
async def upload_image_endpoint(
    file: UploadFile = File(...),
    user: User = Depends(can_upload_image),
    db: AsyncSession = Depends(get_async_session),
) -> ImageUploadResponse:
    """Загружает изображение и возвращает его ID.

    конвертирует в JPG и возвращает UUID.
    """
    image_id = await upload_image(
        db=db,
        file=file,
        username=user.username,
    )
    return ImageUploadResponse(id=image_id)


@router.get(
    '/{image_id}',
    responses={
        200: {"content": {
                "image/jpeg": {},
            }},
        404: {"description": "Изображение не найдено"},
    },
    summary="Получить изображение",
)
async def get_image_endpoint(
    image_id: UUID,
    db: AsyncSession = Depends(get_async_session),
) -> FileResponse:
    """Возвращает изображение по UUID в формате JPG."""
    return await get_image(db=db, image_id=image_id)
