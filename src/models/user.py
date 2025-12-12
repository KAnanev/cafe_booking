from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID

from core.db import Base
from models.mixins import TimestampMixin


class User(SQLAlchemyBaseUserTableUUID, Base):
    """Модель пользователя для хранения данных в базе данных."""
