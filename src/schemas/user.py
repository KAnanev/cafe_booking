from schemas.base import BaseSchema, UUIDIDSchema


class UserShortInfo(UUIDIDSchema, BaseSchema):
    """Краткая информация о пользователе."""

    username: str
    email: str | None = None
    phone: str | None = None
    tg_id: str | None = None
