import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from accounts.auth import UserRole
from crud.cafe_access import CafeAccessCRUD
from managers.exceptions import PermissionDenied
from models.user import User


class CafePermissionService:
    """Сервис доступа к кафе."""

    def __init__(
        self,
        session: AsyncSession,
        cafe_access_crud: CafeAccessCRUD,
    ) -> None:
        """Инициализатор."""
        self._session = session
        self._cafe_access_crud = cafe_access_crud

    async def check_manager_of_cafe(
        self,
        *,
        cafe_id: uuid.UUID,
        user: User,
    ) -> None:
        """Проверяет менеджера к кафе."""
        if user.role != UserRole.MANAGER:
            raise PermissionDenied('Требуется роль MANAGER')

        await self._cafe_access_crud.assert_manager_of_cafe(
            self._session,
            cafe_id=cafe_id,
            manager_id=user.id,
            exc=PermissionDenied('Менеджер не управляет этим кафе'),
        )
