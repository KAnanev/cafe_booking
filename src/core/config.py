from typing import Optional

from pydantic import ConfigDict, EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения для бронирования мест в кафе."""

    app_title: str = 'Бронирование мест в кафе'
    app_desc: str = 'Сервис бронирования мест в кафе'

    postgres_host: str
    postgres_port: int
    postgres_user: str
    postgres_password: str
    postgres_db: str

    secret: str
    first_superuser_email: Optional[EmailStr] = None
    first_superuser_password: Optional[str] = None

    @property
    def database_url(self) -> str:
        """Возвращает URL для асинхронной базы данных (postgresql+asyncpg)."""

        return self._generate_db_url('postgresql+asyncpg')

    @property
    def sync_database_url(self) -> str:
        """Возвращает URL для синхронной базы данных (postgresql)."""

        return self._generate_db_url('postgresql')

    def _generate_db_url(self, protocol: str) -> str:
        """Формирует URL для подключения к базе данных."""
        return (
            f'{protocol}://{self.postgres_user}:{self.postgres_password}'
            f'@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}'
        )

    model_config = ConfigDict(env_file='../infra/.env',
                              env_file_encoding='utf-8',)


settings = Settings()
