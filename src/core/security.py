from pwdlib import PasswordHash

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
