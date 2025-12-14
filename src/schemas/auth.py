from pydantic import BaseModel


class Token(BaseModel):
    """Схема ответа на успешную аутентификацию."""

    access_token: str
    token_type: str
