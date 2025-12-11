from uuid import UUID

from fastapi_users import schemas


class UserRead(schemas.BaseUser[UUID]):
    """Модель для чтения данных пользователя."""


class UserCreate(schemas.BaseUserCreate):
    """Модель для создания нового пользователя."""


class UserUpdate(schemas.BaseUserUpdate):
    """Модель для обновления данных пользователя."""
