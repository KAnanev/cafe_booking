from fastapi import APIRouter

from api.endpoints import auth_router, user_router
from api.endpoints.bookings import router as bookings_router
from api.endpoints.cafes import router as cafes_router
from api.endpoints.dishes import router as dishes_router
from api.endpoints.slots import router as slots_router
from api.endpoints.tables import router as tables_router
from core.constants import AUTH_TAG, USERS_TAG

main_router = APIRouter()

main_router.include_router(
    auth_router,
    prefix='/auth',
    tags=[AUTH_TAG],
)

main_router.include_router(
    user_router,
    prefix='/users',
    tags=[USERS_TAG],
)

main_router.include_router(
    cafes_router,
    prefix='/cafes',
    tags=['Кафе'],
)

main_router.include_router(
    tables_router,
    prefix='/cafes/{cafe_id}/tables',
    tags=['Столы'],
)

main_router.include_router(
    slots_router,
    prefix='/cafes/{cafe_id}/slots',
    tags=['Слоты'],
)

main_router.include_router(
    bookings_router,
    prefix='/booking',
    tags=['Бронирования'],
)

main_router.include_router(
    dishes_router,
    prefix='/dishes',
    tags=['Блюда'],
)
