class UserManagerExceptions(Exception):
    """Доменное исключение."""


class InvalidCredentials(UserManagerExceptions):
    """Исключение, когда пользователь не найден."""


class UserInactive(UserManagerExceptions):
    """Исключение, когда пользователь неактивен."""


class UserNotFound(UserManagerExceptions):
    """Исключение, когда пользователь не найден."""


class PermissionDenied(UserManagerExceptions):
    """Исключение, когда в доступе отказано."""


class UserAlreadyExists(UserManagerExceptions):
    """Исключение, когда пользователь уже существует."""


class BookingNotFound(UserManagerExceptions):
    """Booking or related entity not found."""


class BookingValidationError(UserManagerExceptions):
    """Booking validation error."""


class SlotNotFound(UserManagerExceptions):
    """Slot not found."""


class SlotValidationError(UserManagerExceptions):
    """Slot validation error."""


class CafeNotFound(UserManagerExceptions):
    """Cafe not found."""


class TableNotFound(UserManagerExceptions):
    """Table not found."""
