from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Reservation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    customer_name: str
    table_id: Optional[int] = Field(default=None, foreign_key="table.id", ondelete="CASCADE")
    reservation_time: datetime
    duration_minutes: int
    