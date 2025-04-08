from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import exists

from app.models.database import get_session
from app.models.table import Table
from app.models.reservation import Reservation
from app.schemas.reservation import ReservationRead, ReservationCreate
from app.services.reservation import check_reservation_conflict

router = APIRouter()

@router.get("/reservations/", response_model=list[ReservationRead])
async def read_reservations(session: AsyncSession = Depends(get_session)):
    result = await session.exec(select(Reservation))
    return result.all()

@router.get("/reservations/{reservation_id}", response_model=ReservationRead, include_in_schema=False)
async def read_reservation(
    reservation_id: int, 
    session: AsyncSession = Depends(get_session)
):
    reservation = await session.get(Reservation, reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return reservation

@router.post("/reservations/", response_model=ReservationRead)
async def create_reservation(
    reservation: ReservationCreate, 
    session: AsyncSession = Depends(get_session)
):
    table_exists = await session.exec(
        select(exists().where(Table.id == reservation.table_id))
    )
    
    if not table_exists.one():
        raise HTTPException(
            status_code=400,
            detail=f"Table with id {reservation.table_id} does not exist"
        )
    if await check_reservation_conflict(session, reservation):
        raise HTTPException(status_code=400, detail="Time slot conflicts with existing reservation")
    
    db_reservation = Reservation(**reservation.model_dump())
    session.add(db_reservation)
    await session.commit()
    await session.refresh(db_reservation)
    return db_reservation

@router.delete("/reservations/{reservation_id}")
async def delete_reservation(reservation_id: int, session: AsyncSession = Depends(get_session)):
    reservation = await session.get(Reservation, reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    await session.delete(reservation)
    await session.commit()
    return {"ok": True}