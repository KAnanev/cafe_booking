from dataclasses import dataclass


@dataclass(frozen=True)
class CreateUserCommand:
    """Описывает команду для создания пользователя.

    Хранит данные, необходимые для создания нового пользователя в системе.
    """

    username: str
    password: str
    email: str | None = None
    phone: str | None = None
    tg_id: str | None = None

    def __post_init__(self) -> None:
        """Проверяет наличие email или phone.

        Генерирует исключение, если ни email, ни phone не указаны.
        """
        if not self.email or not self.email:
            raise ValueError('Укажите email или phone')
