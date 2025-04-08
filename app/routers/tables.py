from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.database import get_session
from app.models.table import Table
from app.schemas.table import TableRead, TableCreate

router = APIRouter()

@router.get("/tables/", response_model=list[TableRead])
async def read_tables(session: AsyncSession = Depends(get_session)):
    result = await session.exec(select(Table))
    return result.all()

@router.get("/tables/{table_id}", response_model=TableRead, include_in_schema=False)
async def read_table(table_id: int, session: AsyncSession = Depends(get_session)):
    table = await session.get(Table, table_id)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    return table

@router.post("/tables/", response_model=TableRead)
async def create_table(table: TableCreate, session: AsyncSession = Depends(get_session)):
    db_table = Table(**table.model_dump())
    session.add(db_table)
    await session.commit()
    await session.refresh(db_table)
    return db_table

@router.delete("/tables/{table_id}")
async def delete_table(table_id: int, session: AsyncSession = Depends(get_session)):
    table = await session.get(Table, table_id)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    await session.delete(table)
    await session.commit()
    return {"ok": True}