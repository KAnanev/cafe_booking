import uuid
from io import BytesIO
from pathlib import Path

from PIL import Image as PILImage
from fastapi import HTTPException, UploadFile, status

from core.config import settings
from core.constants import ALLOWED_IMAGE_CONTENT_TYPES, MAX_IMAGE_SIZE


def validate_image(file: UploadFile) -> None:
    """Загруженный файл должен быть в формате JPG или PNG."""
    if file.content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Загружаемый файл должен быть либо в .jpg, либо в .png',
        )


async def read_and_validate_size(file: UploadFile) -> bytes:
    """Читает файл и проверяет, что его размер не превышает MAX_IMAGE_SIZE."""
    content = await file.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail='Размер изображения превышает 5 MB',
        )
    return content


def convert_to_jpg(content: bytes) -> bytes:
    """Преобразует изображение в формат JPEG с качеством 90."""
    try:
        image = PILImage.open(BytesIO(content))
    except (IOError, OSError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Неверный формат файла',
        )

    if image.mode != 'RGB':
        image = image.convert('RGB')

    buffer = BytesIO()
    image.save(buffer, format='JPEG', quality=90)
    buffer.seek(0)
    return buffer.getvalue()


def generate_image_path(image_id: uuid.UUID) -> Path:
    """Генерирует путь для сохранения изображения на основе его UUID."""
    media_root = Path(settings.media_storage_path)
    media_root.mkdir(parents=True, exist_ok=True)
    return media_root / f'{image_id}.jpg'
