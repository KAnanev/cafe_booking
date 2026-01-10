"""FastAPI middleware для автоматического логирования HTTP запросов."""

import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from core.logging.context import clear_user_context
from core.logging.logger import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для автоматического логирования HTTP запросов и ответов."""

    def __init__(self, app: ASGIApp) -> None:
        """Инициализирует middleware."""
        super().__init__(app)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Response],
    ) -> Response:
        """Обрабатывает HTTP запрос и логирует его."""
        start_time = time.time()
        method = request.method
        path = request.url.path
        response: Response | None = None
        exception: Exception | None = None
        try:
            response = await call_next(request)
        except Exception as e:
            exception = e
            raise
        finally:
            process_time = time.time() - start_time
            process_time_ms = int(process_time * 1000)
            status_code = response.status_code if response else 500
            response_details = {
                'method': method,
                'path': path,
                'status_code': status_code,
                'response_time_ms': process_time_ms,
            }
            log_msg = f'HTTP {method} {path} -> {status_code}'
            if exception:
                response_details['exception_type'] = type(exception).__name__
                logger.error(log_msg, exception=exception, **response_details)
            else:
                if status_code >= 500:
                    logger.error(log_msg, **response_details)
                elif status_code >= 400:
                    logger.warning(log_msg, **response_details)
                else:
                    logger.info(log_msg, **response_details)
            clear_user_context()

        return response
