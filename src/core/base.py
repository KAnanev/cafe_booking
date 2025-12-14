"""Импорты класса Base и всех моделей для Alembic."""

from core.db import Base
from models.booking import Booking, BookingStatus
from models.booking_table_slot import BookingTableSlot
from models.cafe import Cafe
from models.slot import TimeSlot
from models.table import CafeTable
from models.user import User

__all__ = [
    "Base",
    "Booking",
    "BookingStatus",
    "BookingTableSlot",
    "Cafe",
    "TimeSlot",
    "CafeTable",
    "User",
]
