from fastapi import APIRouter

from api.endpoints.bookings import router as bookings_router
from api.endpoints.cafes import router as cafes_router
from api.endpoints.slots import router as slots_router
from api.endpoints.tables import router as tables_router

main_router = APIRouter()

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
