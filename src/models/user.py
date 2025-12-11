from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID

from src.core.db import Base


class User(SQLAlchemyBaseUserTableUUID, Base):
    """Модель пользователя для хранения данных в базе данных."""
