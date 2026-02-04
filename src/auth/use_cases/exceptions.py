class InvalidCredentials(Exception):
    """Исключение, возникающее при неверных учетных данных."""

    pass


class UserInactive(Exception):
    """Исключение, возникающее при попытке входа в неактивный аккаунт."""

    pass
