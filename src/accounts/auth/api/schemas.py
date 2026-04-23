from pydantic import BaseModel


class LoginRequest(BaseModel):
    """Схема запроса на аутентификацию."""

    login: str
    password: str


class LoginResponse(BaseModel):
    """Схема ответа на успешную аутентификацию."""

    access_token: str
    token_type: str
