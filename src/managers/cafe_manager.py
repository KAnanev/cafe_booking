import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from crud.cafe import CafeCRUD
from managers.exceptions import CafeNotFound, PermissionDenied
from models import Cafe, User
from models.user import UserRole
from schemas.cafe import CafeCreate, CafeUpdate


class CafeManager:
    """Сервисный слой для чтения кафе с учетом ролей и видимости."""

    def __init__(self, cafe_crud: CafeCRUD, session: AsyncSession) -> None:
        """Инициализирует зависимости: репозиторий Cafe и сессию БД."""
        self._cafe_crud = cafe_crud
        self._session = session

    def _can_view_inactive(self, user: User) -> bool:
        """Возвращает True, если пользователь может видеть неактивные кафе."""
        return (
            bool(getattr(user, 'is_superuser', False))
            or user.role == UserRole.ADMIN
        )

    async def list(self, *, user: User, show_all: bool = False) -> list[Cafe]:
        """Возвращает список кафе в зависимости от роли."""
        if user.role == UserRole.USER:
            return await self._cafe_crud.list(self._session, only_active=True)

        if user.role == UserRole.MANAGER:
            return await self._cafe_crud.list_for_manager(
                self._session,
                manager_id=user.id,
                only_active=True,
            )

        only_active = not (show_all or self._can_view_inactive(user=user))
        return await self._cafe_crud.list(
            self._session,
            only_active=only_active,
        )

    async def create(self, *, user_id: uuid.UUID, obj_in: CafeCreate) -> Cafe:
        """Создает кафе."""
        return await self._cafe_crud.create(
            session=self._session,
            user_id=user_id,
            obj_in=obj_in,
        )

    async def get(self, *, user: User, cafe_id: uuid.UUID) -> Cafe:
        """Возвращает кафе по id с учетом прав."""
        if user.role == UserRole.USER:
            cafe = await self._cafe_crud.get(
                self._session,
                obj_id=cafe_id,
                only_active=True,
            )

        elif user.role == UserRole.MANAGER:
            cafe = await self._cafe_crud.get_for_manager(
                self._session,
                obj_id=cafe_id,
                manager_id=user.id,
                only_active=True,
            )
        else:
            cafe = await self._cafe_crud.get(
                self._session,
                obj_id=cafe_id,
                only_active=False,
            )

        if cafe is None:
            raise CafeNotFound('Кафе не найдено')
        return cafe

    async def update(
        self,
        *,
        user: User,
        cafe_id: uuid.UUID,
        obj_in: CafeUpdate,
    ) -> Cafe:
        """Обновляет кафе. MANAGER может обновлять только своё кафе."""
        if user.role == UserRole.MANAGER:
            cafe = await self._cafe_crud.get_for_manager(
                self._session,
                obj_id=cafe_id,
                manager_id=user.id,
                only_active=True,
            )
            if cafe is None:
                raise CafeNotFound('Кафе не найдено')

            patch = (
                obj_in
                if isinstance(obj_in, dict)
                else obj_in.model_dump(exclude_unset=True)
            )
            if 'is_active' in patch:
                raise PermissionDenied('Менеджер не может менять is_active')

            return await self._cafe_crud.update(
                self._session,
                db_obj=cafe,
                obj_in=patch,
            )

        if user.role == UserRole.ADMIN or getattr(user, 'is_superuser', False):
            cafe = await self._cafe_crud.get(
                self._session,
                obj_id=cafe_id,
                only_active=False,
            )
            if cafe is None:
                raise CafeNotFound('Кафе не найдено')

            return await self._cafe_crud.update(
                self._session,
                db_obj=cafe,
                obj_in=obj_in,
            )

        raise PermissionDenied('Нет прав на обновление кафе')
