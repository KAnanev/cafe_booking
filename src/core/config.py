from pathlib import Path
from typing import Optional

from pydantic import ConfigDict, EmailStr
from pydantic_settings import BaseSettings

from core.openapi import tags_metadata


class Settings(BaseSettings):
    """Настройки приложения для бронирования мест в кафе."""

    app_title: str = 'Бронирование мест в кафе'
    app_desc: str = 'Сервис бронирования мест в кафе'
    openapi_tags: list[dict] = tags_metadata

    postgres_host: str
    postgres_port: int
    postgres_user: str
    postgres_password: str
    postgres_db: str

    secret: str
    algorithm: str
    access_token_expire_minutes: int

    first_superuser_email: Optional[EmailStr] = None
    first_superuser_password: Optional[str] = None

    postgres_db_override: Optional[str] = None

    # Логирование
    log_level: str = 'INFO'
    log_file_path: str = 'logs/app.log'
    log_file_max_size: str = '10 MB'
    log_file_rotation_count: int = 5
    log_file_compression: Optional[str] = None
    log_console_enabled: bool = False
    log_file_enabled: bool = True

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

    model_config = ConfigDict(
        env_file=Path(__file__).parent.parent.parent / 'infra' / '.env',
        env_file_encoding='utf-8',
    )


settings = Settings()
