# src/media/schemas.py
from uuid import UUID
from pydantic import BaseModel


class ImageUploadResponse(BaseModel):
    id: UUID
