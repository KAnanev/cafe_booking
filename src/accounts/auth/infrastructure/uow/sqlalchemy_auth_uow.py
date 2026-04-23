from shared.infrastructure.repositories.sqlalchemy_user_repository import (
    SqlAlchemyUserRepository,
)
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from auth.infrastructure.repositories.sqlalchemy_session_repository import (
    SqlAlchemySessionRepository,
)


class SqlAlchemyAuthUnitOfWork:
    """Работа предоставляет методы для управления аутентификацией с БД.

    Класс используется для взаимодействия с репозиториями пользователей и
    сессий в рамках одного асинхронного контекста и гарантирует их
    корректную работу.

    Attributes:
        session: Текущая асинхронная сессия работы с БД.
        users: Репозиторий для управления пользователями.
        sessions: Репозиторий для управления пользовательскими сессиями.

    """

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        """Инициализирует экземпляр класса с учетом фабрики сессий."""
        self._session_factory = session_factory
        self.session: AsyncSession | None = None

        self.users: SqlAlchemyUserRepository | None = None
        self.sessions: SqlAlchemySessionRepository | None = None

    async def __aenter__(self) -> 'SqlAlchemyAuthUnitOfWork':
        self.session = self._session_factory()
        self.users = SqlAlchemyUserRepository(self.session)
        self.sessions = SqlAlchemySessionRepository(self.session)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None:
        if self.session is None:
            return

        if exc_type:
            await self.session.rollback()

        await self.session.close()

    async def commit(self) -> None:
        """Сохраняет изменения в базе данных в асинхронном режиме.

        Raises:
            RuntimeError: Если сессия не инициализирована.

        """
        if self.session is None:
            raise RuntimeError('Session is not initialized.')
        await self.session.commit()

    async def rollback(self) -> None:
        """Откатывает изменения текущей сессии к предыдущему состоянию.

        Raises:
            RuntimeError: Если сессия не была инициализирована.

        """
        if self.session is None:
            raise RuntimeError('Session is not initialized.')
        await self.session.rollback()
