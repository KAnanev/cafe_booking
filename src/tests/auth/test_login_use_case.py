import pytest

from auth.domain.password import PasswordService
from auth.providers.user_provider import UserProvider
from auth.use_cases.exceptions import InvalidCredentials, UserInactive
from auth.use_cases.login import LoginUseCase


class FakeUser:
    """Фиктивный пользователь для тестирования."""

    def __init__(
        self,
        *,
        _id: int = 1,
        hashed_password: str = 'hash',
        is_active: bool = True,
    ) -> None:
        """Инициализирует фиктивного пользователя для тестирования."""
        self.id = _id
        self.hashed_password = hashed_password
        self.is_active = is_active


class FakeDBUserProvider:
    """Фиктивный репозиторий пользователей для тестирования."""

    def __init__(self, user: FakeUser | None) -> None:
        """Инициализирует фиктивный репозиторий пользователей."""
        self._user = user

    async def get_by_login(self, login: str) -> FakeUser | None:
        """Фиктивный метод получения пользователя по логину."""
        return self._user


class FakePasswordService:
    """Фиктивный сервис проверки пароля для тестирования."""

    def __init__(self, valid: bool) -> None:
        """Фиктивный сервис проверки пароля для тестирования."""
        self._valid = valid

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """Фиктивная проверка пароля."""
        return self._valid

    def hash(self, plain_password: str) -> str:
        """Фиктивная хэш-функция для пароля."""
        return 'fake-hash'


@pytest.mark.asyncio
async def test_login_success() -> None:
    """Тест проверяет успешный сценарий логина пользователя."""
    user = FakeUser(is_active=True)
    repo: UserProvider = FakeDBUserProvider(user)
    password_service: PasswordService = FakePasswordService(valid=True)

    use_case = LoginUseCase(repo, password_service)

    result = await use_case.execute(login='test', password='password')

    assert result is user


@pytest.mark.asyncio
async def test_login_user_not_found() -> None:
    """Тест проверяет сценарий, когда пользователь не найден."""
    repo = FakeDBUserProvider(user=None)
    password_service = FakePasswordService(valid=True)

    use_case = LoginUseCase(repo, password_service)

    with pytest.raises(InvalidCredentials):
        await use_case.execute(login='test', password='password')


@pytest.mark.asyncio
async def test_login_invalid_password() -> None:
    """Тест проверяет сценарий, когда пароль неверный."""
    user = FakeUser(is_active=True)
    repo = FakeDBUserProvider(user)
    password_service = FakePasswordService(valid=False)

    use_case = LoginUseCase(repo, password_service)

    with pytest.raises(InvalidCredentials):
        await use_case.execute(login='test', password='wrong')


@pytest.mark.asyncio
async def test_login_user_inactive() -> None:
    """Тест проверяет сценарий, когда пользователь не активен."""
    user = FakeUser(is_active=False)
    repo = FakeDBUserProvider(user)
    password_service = FakePasswordService(valid=True)

    use_case = LoginUseCase(repo, password_service)

    with pytest.raises(UserInactive):
        await use_case.execute(login='test', password='password')
