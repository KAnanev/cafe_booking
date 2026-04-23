from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()


class SecurePasswordService:
    """Сервис для обработки паролей."""

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """Проверяет, соответствует ли открытый пароль хешу."""
        return password_hash.verify(plain_password, hashed_password)

    def hash(self, plain_password: str) -> str:
        """Генерирует криптографический хеш из пароля."""
        return password_hash.hash(plain_password)
