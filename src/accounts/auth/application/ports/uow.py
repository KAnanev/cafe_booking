from typing import Any, Protocol

from accounts.auth.application.ports.session_repository import (
    SessionRepository,
)
from accounts.auth.application.ports.user_reader import UserRepository


class AuthUnitOfWork(Protocol):
    """Протокол для управления единицей работы в контексте аутентификации.

    Представляет собой интерфейс управления операциями с пользователями
    и сессиями в рамках единого контекста. Предоставляет методы для работы
    с ресурсами в асинхронном коде.
    """

    users: UserRepository
    sessions: SessionRepository

    async def __aenter__(self) -> 'AuthUnitOfWork':
        """Асинхронный метод для входа в контекстный менеджер.

        Вызывается при использовании объекта в конструкциях async with.

        Returns:
            AuthUnitOfWork: Возвращает экземпляр текущего класса.

        """

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Завершает асинхронный контекстный менеджер.

        Метод вызывается при выходе из контекста, как часть работы
        контекстного менеджера.

        Args:
            exc_type: Тип исключения, если оно было брошено.
            exc_val: Объект исключения, если было брошено исключение.
            exc_tb: Трассировка стека исключения, если оно было брошено.

        """

    async def commit(self) -> None:
        """Фиксирует текущую транзакцию в базе данных.

        Осуществляет завершение текущей транзакции, сохраняя все изменения.
        """

    async def rollback(self) -> None:
        """Возвращает систему в начальное состояние, откатывая изменения."""
