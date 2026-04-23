from typing import Protocol

from shared.application.ports.uow import UnitOfWork

from accounts.auth.application.ports.session_repository import (
    SessionRepository,
)
from accounts.auth.application.ports.user_reader import UserRepository


class AuthUnitOfWork(UnitOfWork, Protocol):
    """Хранит интерфейс для работы с агрегатами аутентификации.

    Предоставляет доступ к репозиториям пользователей и сессий.
    """

    users: UserRepository
    sessions: SessionRepository
