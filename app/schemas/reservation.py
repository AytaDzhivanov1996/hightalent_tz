from datetime import datetime
from pydantic import BaseModel

class ReservationBase(BaseModel):
    customer_name: str
    table_id: int
    reservation_time: datetime
    duration_minutes: int

class ReservationCreate(ReservationBase):
    pass

class ReservationRead(ReservationBase):
    id: int

class ReservationUpdate(ReservationBase):
    pass