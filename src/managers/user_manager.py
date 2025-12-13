from sqlalchemy.ext.asyncio import AsyncSession

from core.security import get_password_hash
from crud.user import user_crud
from schemas.user import UserCreate, UserCreateInternal, UserDB


class UserManager:
    """Менеджер пользователей."""

    def __init__(self, session: AsyncSession) -> None:
        """Инициализирует менеджер сессией базы данных."""
        self.session = session

    async def create_user(self, user: UserCreate) -> UserDB:
        """Создаёт нового пользователя с проверкой уникальности.

        Проверяются поля email и телефона.
        """
        if user.email is not None:
            existing_by_email = await user_crud.get_by_email(
                user.email,
                session=self.session,
            )
            if existing_by_email:
                raise ValueError(f'Пользователь {user.email} уже существует')

        if user.phone is not None:
            existing_by_phone = await user_crud.get_by_phone(
                user.phone,
                session=self.session,
            )
            if existing_by_phone:
                raise ValueError(f'Пользователь {user.phone} уже существует')

        hashed_password = get_password_hash(user.password)
        user_internal = UserCreateInternal(
            **user.model_dump(exclude={'password'}),
            hashed_password=hashed_password,
        )
        db_user = await user_crud.create(
            obj_in=user_internal,
            session=self.session,
        )
        return UserDB.model_validate(db_user)
