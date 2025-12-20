import logging
import uuid

from fastapi import HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from media.models import Image
from media.utils import (
    convert_to_jpg,
    generate_image_path,
    read_and_validate_size,
    validate_image,
)

logger = logging.getLogger(__name__)


async def upload_image(
    db: AsyncSession,
    file: UploadFile,
    username: str | None = None,
) -> uuid.UUID:
    """Загружает изображение, конвертирует в JPG и сохраняет в БД."""
    try:
        validate_image(file)

        content = await read_and_validate_size(file)
        jpg_content = convert_to_jpg(content)

        image_id = uuid.uuid4()
        path = generate_image_path(image_id)

        # Create directory if it doesn't exist
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(jpg_content)

        image = Image(
            id=image_id,
            file_path=str(path),
        )
        db.add(image)
        await db.flush()
        await db.commit()

        logger.info(
            'Image uploaded',
            extra={
                'image_id': str(image_id),
                'user': username or 'SYSTEM',
            },
        )

        return image_id

    except Exception as e:
        await db.rollback()
        logger.error(
            f'Image upload failed: {str(e)}',
            extra={'user': username or 'SYSTEM'},
        )
        raise


async def get_image(
    db: AsyncSession,
    image_id: uuid.UUID,
) -> FileResponse:
    """Получает изображение по UUID и возвращает в виде файла."""
    image = await db.get(Image, image_id)

    if not image or not image.active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Image not found',
        )

    return FileResponse(
        image.file_path,
        media_type='image/jpeg',
        filename=f'{image_id}.jpg',
    )
