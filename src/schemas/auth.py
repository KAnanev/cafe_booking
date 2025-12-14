from pydantic import BaseModel


class AuthRequest(BaseModel):
    """Схема запроса на аутентификацию."""

    login: str
    password: str


class AuthResponse(BaseModel):
    """Схема ответа на успешную аутентификацию."""

    access_token: str
    token_type: str
