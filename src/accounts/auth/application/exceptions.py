class AuthenticationFailed(Exception):
    """Исключение, возникающее при неверных учетных данных."""


class InactiveAccount(Exception):
    """Исключение, возникающее при попытке входа в неактивный аккаунт."""
