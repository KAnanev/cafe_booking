from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from api.exceptions import (
    InvalidCredentialsHTTP,
    UserInactiveHTTP,
    UserNotFoundHTTP,
)
from core.db import get_async_session
from core.exceptions import InvalidToken
from core.security import decode_access_token
from crud.user import user_crud
from models.user import User
from core.logging import set_user_context

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')


async def get_current_user(
    session: AsyncSession = Depends(get_async_session),
    token: str = Depends(oauth2_scheme),
) -> User:
    """Получение текущего аутентифицированного пользователя.

    Извлекает JWT access-токен из заголовка Authorization,
    декодирует его, загружает пользователя из базы данных
    и проверяет его активность.
    """
    try:
        user_id = decode_access_token(token)
    except InvalidToken:
        raise InvalidCredentialsHTTP()

    user = await user_crud.get_by_id(obj_id=user_id, session=session)
    if not user:
        raise UserNotFoundHTTP()

    if not user.is_active:
        raise UserInactiveHTTP()
    # Устанавливаем контекст пользователя для логирования
    set_user_context(
        user_id=user.id,
        username=user.email,
        email=user.email,
        role=user.role.name if hasattr(user.role, 'name') else str(user.role),
    )
    return user


# def required_role(role: UserRoles) -> Callable[[User], Awaitable[User]]:
#     """Возвращает зависимость, проверяющую минимальную роль пользователя."""
#
#     async def check_role(user: User = Depends(get_current_user)) -> User:
#         if user.role < role:
#             raise HTTPException(
#                 status_code=HTTPStatus.FORBIDDEN,
#                 detail='Недостаточно прав.',
#             )
#         return user
#
#     return check_role
