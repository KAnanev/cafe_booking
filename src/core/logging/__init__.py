"""Модуль логирования для приложения."""

from loguru import logger as loguru_logger

from core.config import settings
from core.logging.context import (
    UserContext,
    clear_user_context,
    get_user_context,
    set_user_context,
)
from core.logging.handlers import setup_console_handler, setup_file_handler
from core.logging.logger import AppLogger, logger
from core.logging.middleware import LoggingMiddleware


def setup_logging() -> None:
    """Инициализирует и настраивает логирование при старте приложения."""
    loguru_logger.remove()
    file_handler_id = setup_file_handler()
    console_handler_id = setup_console_handler()
    if file_handler_id is None and console_handler_id is None:
        loguru_logger.add(
            sink="stderr",
            level=settings.log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
            enqueue=True,
        )
        loguru_logger.warning(
            "Все обработчики логов отключены. "
            "Используется минимальный обработчик в stderr.",
        )
    logger.info(
        "Модуль логирования инициализирован",
        log_level=settings.log_level,
        file_enabled=settings.log_file_enabled,
        console_enabled=settings.log_console_enabled,
        file_path=(
            settings.log_file_path if settings.log_file_enabled else None
        ),
        file_handler_id=file_handler_id,
        console_handler_id=console_handler_id,
    )


__all__ = [
    "logger",
    "AppLogger",
    "setup_logging",
    "UserContext",
    "get_user_context",
    "set_user_context",
    "clear_user_context",
    "LoggingMiddleware",
]
