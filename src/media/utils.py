import uuid
from pathlib import Path
from io import BytesIO

from fastapi import UploadFile, HTTPException, status
from PIL import Image as PILImage

from core.config import settings
from core.constant import MAX_IMAGE_SIZE, ALLOWED_IMAGE_CONTENT_TYPES


def validate_image(file: UploadFile) -> None:
    if file.content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPG and PNG images are allowed",
        )


async def read_and_validate_size(file: UploadFile) -> bytes:
    content = await file.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image size exceeds 5 MB",
        )
    return content


def convert_to_jpg(content: bytes) -> bytes:
    try:
        image = PILImage.open(BytesIO(content))
    except (IOError, OSError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image file",
        )

    if image.mode != "RGB":
        image = image.convert("RGB")

    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=90)
    buffer.seek(0)
    return buffer.getvalue()


def generate_image_path(image_id: uuid.UUID) -> Path:
    media_root = Path(settings.media_storage_path)
    media_root.mkdir(parents=True, exist_ok=True)
    return media_root / f"{image_id}.jpg"
