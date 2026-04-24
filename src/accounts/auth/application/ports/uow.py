from typing import Protocol

from shared.application.ports.uow import UnitOfWork
from shared.application.ports.user_repository import UserRepository

from accounts.auth.application.ports.session_repository import (
    SessionRepository,
)


class AuthUnitOfWork(UnitOfWork, Protocol):
    """Хранит интерфейс для работы с агрегатами аутентификации.

    Предоставляет доступ к репозиториям пользователей и сессий.
    """

    users: UserRepository
    sessions: SessionRepository
