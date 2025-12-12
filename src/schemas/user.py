from uuid import UUID

from fastapi_users import schemas

from schemas.base import TimestampSchema


class UserMixin(TimestampSchema):
    username: str
    email: str
    phone: str
    tg_id: str
    role: int


class UserRead(UserMixin, schemas.BaseUser[UUID]):
    """Модель для чтения данных пользователя."""


class UserCreate(schemas.BaseUserCreate):
    """Модель для создания нового пользователя."""


class UserUpdate(schemas.BaseUserUpdate):
    """Модель для обновления данных пользователя."""
