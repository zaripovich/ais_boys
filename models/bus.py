from __future__ import annotations

import asyncio
from time import sleep
from typing import List

from pydantic import BaseModel, Field
from sqlalchemy import (
    Boolean,
    Column,
    Float,
    Integer,
    delete,
    insert,
    select,
    update,
)
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from db import Base, DbResult


class BusSchema(BaseModel):
    id: int = Field(exclude=False, title="id")
    price: float = Field(exclude=False, title="price")
    status: bool = Field(exclude=False, title="status")


# pylint: disable=E0213,C0115,C0116,W0718
class Bus(Base):
    __tablename__ = "buses"

    id = Column(Integer, autoincrement=True, primary_key=True)
    price = Column(Float)
    status = Column(Boolean)

    async def add_first(self, session: AsyncSession) -> DbResult:
        try:
            result = await session.execute(insert(Bus).values((self.id,self.price,self.status)))
            if result.is_insert:
                await session.commit()
                return DbResult.result(self.id)
            else:
                raise "Error"
        except Exception as e:
            await session.rollback()
            return DbResult.error(str(e), False)
        
    
    async def add(self, session: AsyncSession) -> DbResult:
        try:
            session.add(self)
            await session.commit()
            return DbResult.result(self.id)
        except Exception as e:
            await session.rollback()
            return DbResult.error(str(e), False)
        


    def auto_open(session: AsyncSession, bus_id: int) -> DbResult:
        sleep(5)
        try:
            asyncio.run(Bus.set_active(session,bus_id,True))
            return DbResult.result()
        except Exception as e:
            return DbResult.error(str(e))

    async def get_by_id(session: AsyncSession, bus_id: int) -> DbResult:
        try:
            result = await session.execute(select(Bus).where(Bus.id == bus_id))
            data = result.scalars().first()
            await session.commit()
            return DbResult.result(data)
        except Exception as e:
            return DbResult.error(str(e))
        
    
    async def set_active(session: AsyncSession, bus_id: int, status: bool) -> DbResult:
        try:
            await session.execute(update(Bus).where(Bus.id == bus_id).values(status=status))
            await session.commit()
            return DbResult.result()
        except Exception as e:
            return DbResult.error(str(e))
        
    
    async def set_price(session: AsyncSession, bus_id: int, price: float) -> DbResult:
        try:
            await session.execute(update(Bus).where(Bus.id == bus_id).values(price=price))
            await session.commit()
            return DbResult.result()
        except Exception as e:
            return DbResult.error(str(e))

    async def get_all(session: AsyncSession) -> DbResult:
        try:
            result = await session.execute(select(Bus))
            data = result.scalars().all()
            await session.commit()
            return DbResult.result(data)
        except Exception as e:
            return DbResult.error(str(e))
        
    async def delete(session: AsyncSession, id: int) -> DbResult:
        try:
            _ = await session.execute(delete(Bus).where(Bus.id == id))
            await session.commit()
            return DbResult.result(True)
        except Exception as e:
            await session.rollback()
            return DbResult.error(str(e), False)
    


    def from_one_to_schema(bus: Bus) -> BusSchema:
        try:
            bus_schema = BusSchema(
                id=bus.id,
                price=bus.price,
                status=bus.status
            )
            return bus_schema
        except Exception:
            return None

    def from_list_to_schema(buss: List[Bus]) -> list[BusSchema]:
        try:
            return [Bus.from_one_to_schema(b) for b in buss]
        except Exception:
            return []


async def init_bus(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
