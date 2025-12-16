from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

from core.config import settings
from core.exceptions import InvalidToken

password_hash = PasswordHash.recommended()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет, соответствует ли открытый пароль хешу.

    Использует безопасное сравнение, устойчивое к тайминг-атакам.
    Поддерживает автоматическое обновление устаревших хешей.

    Args:
        plain_password: Пароль в открытом виде (как ввёл пользователь).
        hashed_password: Хеш пароля, сохранённый в базе данных.

    Returns:
        True, если пароль верен; False — в противном случае.

    """
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Генерирует криптографический хеш из пароля.

    Использует адаптивный алгоритм (например, Argon2id или bcrypt),
    с автоматической солью и настройками по умолчанию, рекомендованными
    библиотекой pwdlib для обеспечения безопасности.

    Args:
        password: Пароль в открытом виде.

    Returns:
        Строка с хешем пароля (включает алгоритм, соль и хеш в кодировке).

    """
    return password_hash.hash(password)


def create_access_token(
    user_id: UUID,
    expires_delta: timedelta | None = None,
) -> str:
    """Создаёт JWT access-токен.

    В токене хранится только идентификатор пользователя (sub),
    без ролей и бизнес-данных.
    """
    now = datetime.now(timezone.utc)

    expire = (
        now + expires_delta
        if expires_delta
        else now + timedelta(minutes=settings.access_token_expire_minutes)
    )

    payload = {
        'sub': str(user_id),
        'iat': now,
        'exp': expire,
    }

    return jwt.encode(
        payload,
        settings.secret,
        algorithm=settings.algorithm,
    )


def decode_access_token(token: str) -> UUID:
    """Декодирует и валидирует JWT access-токен.

    Проверяет:
    - корректность подписи
    - срок действия токена (exp)
    - наличие и корректность поля sub
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret,
            algorithms=[settings.algorithm],
        )

        user_id_str = payload.get('sub')
        if not user_id_str:
            raise InvalidToken

        return UUID(user_id_str)

    except (InvalidTokenError, ValueError):
        raise InvalidToken
