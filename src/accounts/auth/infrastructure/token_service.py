from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt

from core.config import settings
from core.constants import ACCESS_TOKEN_TTL


class SecureTokenService:
    """Сервис для создания защищённых токенов."""

    def create_access_token(
        self,
        user_id: UUID,
        user_session_id: UUID,
    ) -> str:
        """Создаёт JWT access-токен.

        В токене хранится только идентификатор пользователя (sub),
        без ролей и бизнес-данных.
        """
        now = datetime.now(timezone.utc)

        payload = {
            'sub': str(user_id),
            'iat': int(now.timestamp()),
            'exp': int(
                (now + timedelta(seconds=ACCESS_TOKEN_TTL)).timestamp(),
            ),
            'sid': str(user_session_id),
        }

        return jwt.encode(
            payload,
            settings.secret,
            algorithm=settings.algorithm,
        )
