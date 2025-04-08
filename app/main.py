from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import SQLModel

from app.models.database import engine
from app.routers import tables, reservations

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(lifespan=lifespan)

app.include_router(tables.router)
app.include_router(reservations.router)