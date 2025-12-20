class UserManagerExceptions(Exception):
    """Доменное исключение."""


class InvalidCredentials(UserManagerExceptions):
    """Исключение, когда пользователь не найден."""


class UserInactive(UserManagerExceptions):
    """Исключение, когда пользователь неактивен."""


class PermissionDenied(UserManagerExceptions):
    """Исключение, когда в доступе отказано."""


class UserAlreadyExists(UserManagerExceptions):
    """Исключение, когда пользователь уже существует."""


class BookingNotFound(UserManagerExceptions):
    """Booking or related entity not found."""


class BookingValidationError(UserManagerExceptions):
    """Booking validation error."""
