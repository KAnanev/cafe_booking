from dataclasses import dataclass


@dataclass(frozen=True)
class LoginCommand:
    """Класс для хранения данных аутентификации."""

    login: str
    password: str


@dataclass(frozen=True)
class LoginResult:
    """Класс для хранения данных ответа при успешной авторизации."""

    access_token: str
    token_type: str = 'Bearer'
