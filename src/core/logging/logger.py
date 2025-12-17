"""Основной класс логгера для приложения."""

import json
from typing import Any, Optional

from loguru import logger as loguru_logger

from core.logging.context import get_user_context


class AppLogger:
    """Обертка над loguru logger с автоизвлечением контекста пользователя."""

    def __init__(self) -> None:
        """Инициализирует экземпляр логгера."""
        self._logger = loguru_logger

    def _format_event_details(self, **kwargs: Any) -> str:
        """Форматирует дополнительные параметры в строку для event_details."""
        if not kwargs:
            return ''
        filtered_kwargs = {k: v for k, v in kwargs.items() if v is not None}
        if not filtered_kwargs:
            return ''
        try:
            return json.dumps(filtered_kwargs, ensure_ascii=False, default=str)
        except (TypeError, ValueError):
            return str(filtered_kwargs)

    def _get_extra(self, **kwargs: Any) -> dict[str, Any]:
        """Формирует словарь extra с инфо о пользователе и деталями события."""
        user_context = get_user_context()
        user_info = user_context.to_user_info()
        extra: dict[str, Any] = {
            'user_info': user_info,
            'event_details': self._format_event_details(**kwargs),
        }
        return extra

    def info(self, message: str, **kwargs: Any) -> None:
        """Логирует информационное сообщение."""
        self._logger.info(message, **self._get_extra(**kwargs))

    def error(
        self,
        message: str,
        exception: Optional[Exception] = None,
        **kwargs: Any,
    ) -> None:
        """Логирует сообщение об ошибке."""
        extra = self._get_extra(**kwargs)
        if exception:
            self._logger.exception(message, **extra)
        else:
            self._logger.error(message, **extra)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Логирует предупреждение."""
        self._logger.warning(message, **self._get_extra(**kwargs))

    def debug(self, message: str, **kwargs: Any) -> None:
        """Логирует отладочное сообщение."""
        self._logger.debug(message, **self._get_extra(**kwargs))

    def critical(self, message: str, **kwargs: Any) -> None:
        """Логирует критическую ошибку."""
        self._logger.critical(message, **self._get_extra(**kwargs))


logger = AppLogger()
