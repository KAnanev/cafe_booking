import uuid

from users.domain.user import User

from auth.application.ports.security import PasswordService


class RegisterUserCommand:
    """Хранит данные для регистрации пользователя.

    Предназначен для передачи информации о новом пользователе в систему.
    """

    username: str
    password: str
    email: str | None
    phone: str | None
    tg_id: str | None


class RegisterUserResult:
    """Хранит данные о результате регистрации пользователя.

    Представляет данные о зарегистрированном пользователе, включая id,
    имя пользователя, email, телефон, Telegram ID, роль, статус активности,
    а также дату создания и изменения записи.
    """

    id: uuid.UUID
    username: str
    email: str | None
    phone: str | None
    tg_id: str | None
    role: str
    is_active: bool
    created_at: str
    updated_at: str


class RegisterUserUseCase:
    """Класс регистрации пользователя."""

    def __init__(
        self,
        password_service: PasswordService,
    ) -> None:
        """Инициализация класса RegisterUserUseCase."""
        self.password_service = password_service

    def execute(self, command: RegisterUserCommand) -> User:
        """Выполняет регистрацию пользователя.

        Создаёт нового пользователя с указанными данными, хэшируя пароль.
        """
        hashed_password = self.password_service.hash(command.password)

        return User.create_user(
            username=command.username,
            hashed_password=hashed_password,
            email=command.email,
            phone=command.phone,
            tg_id=command.tg_id,
        )
