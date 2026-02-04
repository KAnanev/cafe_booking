from api.dependencies.auth import require_auth

# Просто алиас для require_auth, если нужно семантическое имя
get_current_active_user = require_auth


# from typing import Optional

# from fastapi import Depends, HTTPException, status

# from api.dependencies.auth import get_optional_user
# from models import User


# async def get_current_active_user(
#     user: Optional[User] = Depends(get_optional_user),
# ) -> User:
#     """Возвращает аутентифицированного юзера или вызывает 401 ошибку."""
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail='Not authenticated',
#         )
#     return user
