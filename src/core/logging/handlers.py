"""Обработчики логов для файла и консоли."""

import sys
from pathlib import Path
from typing import Optional

from loguru import logger

from core.config import settings
from core.logging.formatters import create_log_format


def setup_file_handler() -> Optional[int]:
    """Настраивает файловый обработчик логов с ротацией."""
    if not settings.log_file_enabled:
        return None
    log_file_path = Path(settings.log_file_path)
    log_dir = log_file_path.parent
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        logger.error(
            f'Не удалось создать директорию для логов: {log_dir}: {e}',
        )
        raise
    log_format = create_log_format()
    return logger.add(
        sink=str(log_file_path),
        format=log_format,
        level=settings.log_level,
        rotation=settings.log_file_max_size,
        retention=settings.log_file_rotation_count,
        compression=settings.log_file_compression,
        enqueue=True,
        backtrace=True,
        diagnose=True,
        encoding='utf-8',
    )


def setup_console_handler() -> Optional[int]:
    """Настраивает консольный обработчик логов."""
    if not settings.log_console_enabled:
        return None
    log_format = create_log_format()
    return logger.add(
        sink=sys.stderr,
        format=log_format,
        level=settings.log_level,
        colorize=True,
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )
