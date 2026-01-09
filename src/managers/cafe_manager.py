from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from crud.cafe import CafeCRUD
from crud.cafe_access import cafe_access_crud
from managers.exceptions import (
    CafeNotFound,
    InvalidCredentials,
    PermissionDenied,
)
from models import Cafe, User
from models.user import UserRole
from schemas.cafe import CafeCreate, CafeUpdate


class CafeManager:
    """Сервисный слой для чтения кафе с учетом ролей и видимости."""

    def __init__(self, cafe_crud: CafeCRUD, session: AsyncSession) -> None:
        """Инициализирует зависимости: репозиторий Cafe и сессию БД."""
        self._cafe_crud = cafe_crud
        self._session = session

    async def list_cafe(
        self,
        *,
        user: User,
        show_all: bool = False,
    ) -> list[Cafe]:
        """Возвращает список кафе в зависимости от роли."""
        if user.role == UserRole.USER:
            return await self._cafe_crud.list_for_user(self._session)

        only_active = not show_all

        if user.role == UserRole.MANAGER:
            return await self._cafe_crud.list_for_manager(
                self._session,
                manager_id=user.id,
                only_active=only_active,
            )

        return await self._cafe_crud.list(
            self._session,
            only_active=only_active,
        )

    async def get(self, *, user: User, cafe_id: uuid.UUID) -> Cafe:
        """Возвращает кафе."""
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
                only_active=False,
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

    async def create(self, *, user_id: uuid.UUID, obj_in: CafeCreate) -> Cafe:
        """Создает кафе."""
        validated = await self._validate_managers_ids(
            managers_id=obj_in.managers_id,
        )
        obj_in = obj_in.model_copy(update={'managers_id': validated})
        return await self._cafe_crud.create(
            session=self._session,
            user_id=user_id,
            obj_in=obj_in,
        )

    async def update(
        self,
        *,
        user: User,
        cafe_id: uuid.UUID,
        obj_in: CafeUpdate,
    ) -> Cafe:
        """Обновляет кафе."""
        cafe = await self.get(user=user, cafe_id=cafe_id)

        if cafe is None:
            raise CafeNotFound('Кафе не найдено')

        if user.role == UserRole.MANAGER:
            await cafe_access_crud.assert_manager_of_cafe(
                self._session,
                cafe_id=cafe_id,
                manager_id=user.id,
                exc=PermissionDenied('Менеджер не управляет этим кафе'),
            )

            if 'is_active' in obj_in.model_fields_set:
                raise PermissionDenied('Менеджер не может менять is_active')
            if 'managers_id' in obj_in.model_fields_set:
                raise PermissionDenied('Менеджер не может менять managers_id')

        managers_provided = 'managers_id' in obj_in.model_fields_set

        if managers_provided:
            validated = await self._validate_managers_ids(
                managers_id=obj_in.managers_id,
            )
            obj_in = obj_in.model_copy(update={'managers_id': validated})

        return await self._cafe_crud.update(
            self._session,
            db_obj=cafe,
            obj_in=obj_in,
        )

    async def _validate_managers_ids(
        self,
        *,
        managers_id: list[uuid.UUID],
    ) -> list[uuid.UUID]:
        if not managers_id:
            return []

        unique_ids: list[uuid.UUID] = list(dict.fromkeys(managers_id))

        stmt = select(User.id, User.role).where(User.id.in_(unique_ids))
        rows = (await self._session.execute(stmt)).all()
        found = {user_id: role for user_id, role in rows}

        for unique_id in unique_ids:
            if unique_id not in found:
                raise InvalidCredentials()
            if found[unique_id] != UserRole.MANAGER:
                raise InvalidCredentials()

        return unique_ids
