from fastapi import APIRouter

from api.endpoints.bookings import router as booking_router

main_router = APIRouter()

main_router.include_router(booking_router)
