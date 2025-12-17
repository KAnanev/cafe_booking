"""Контекст пользователя для логирования в асинхронном окружении FastAPI."""

from contextvars import ContextVar
from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass
class UserContext:
    """Контейнер для информации о пользователе в контексте запроса."""

    user_id: Optional[UUID] = None
    username: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None

    def to_user_info(self) -> str:
        """Форматирует информацию о пользователе для логирования."""
        if self.user_id is None:
            return 'SYSTEM'
        username = self.username or self.email or 'Unknown'
        return f'{username}({self.user_id})'

    def is_set(self) -> bool:
        """Проверяет, установлен ли контекст пользователя."""
        return self.user_id is not None


_user_context: ContextVar[Optional[UserContext]] = ContextVar(
    'user_context',
    default=None,
)


def get_user_context() -> UserContext:
    """Получает контекст пользователя из текущего контекста выполнения."""
    context = _user_context.get()
    if context is None:
        return UserContext()
    return context


def set_user_context(
    user_id: Optional[UUID] = None,
    username: Optional[str] = None,
    email: Optional[str] = None,
    role: Optional[str] = None,
) -> None:
    """Устанавливает контекст пользователя для текущего запроса."""
    context = UserContext(
        user_id=user_id,
        username=username,
        email=email,
        role=role,
    )
    _user_context.set(context)


def clear_user_context() -> None:
    """Очищает контекст пользователя для текущего запроса."""
    _user_context.set(None)
