from models.booking import Booking
from schemas.booking import BookingInfo, TablesSlotsInfo
from schemas.cafe import CafeShort
from schemas.slot import TimeSlotShort
from schemas.table import TableShort


def build_booking_info(booking: Booking) -> BookingInfo:
    """Приводит Booking к BookingInfo с краткой информацией."""
    cafe_short = CafeShort.model_validate(
        booking.cafe,
        from_attributes=True,
    )
    tables_slots = []
    for link in booking.tables_slots:
        table_short = TableShort.model_validate(
            link.table,
            from_attributes=True,
        )
        slot_short = TimeSlotShort.model_validate(
            link.slot,
            from_attributes=True,
        )
        tables_slots.append(
            TablesSlotsInfo.model_validate(
                {
                    **link.__dict__,
                    'table': table_short,
                    'slot': slot_short,
                },
                from_attributes=True,
            ),
        )

    return BookingInfo.model_validate(
        {
            **booking.__dict__,
            'user': None,
            'cafe': cafe_short,
            'tables_slots': tables_slots,
        },
        from_attributes=True,
    )
