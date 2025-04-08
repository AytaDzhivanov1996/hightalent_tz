from datetime import timedelta
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.reservation import Reservation
from app.schemas.reservation import ReservationCreate
from sqlmodel import select, and_

async def check_reservation_conflict(
    session: AsyncSession, 
    new_reservation: ReservationCreate
) -> bool:
    start_time = new_reservation.reservation_time
    end_time = start_time + timedelta(minutes=new_reservation.duration_minutes)

    existing = await session.exec(
        select(Reservation)
        .where(
            Reservation.table_id == new_reservation.table_id,
            and_(
                Reservation.reservation_time < end_time,
                Reservation.reservation_time + 
                (Reservation.duration_minutes * timedelta(minutes=1)) > start_time
            )
        )
    )
    return existing.first() is not None