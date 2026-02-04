class TokenService:
    """Токен-сервис для работы с JWT-токенами."""

    def create_access_token(self, user_id: int) -> str:
        """Создает JWT-токен для доступа."""
        ...
