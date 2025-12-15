class InvalidCredentials(Exception):
    """Исключение, когда пользователь не найден."""


class UserInactive(Exception):
    """Исключение, когда пользователь неактивен."""


class PermissionDenied(Exception):
    """Исключение, когда в доступе отказано."""


class UserAlreadyExists(Exception):
    """Исключение, когда пользователь уже существует."""
