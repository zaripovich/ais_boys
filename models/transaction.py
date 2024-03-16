from __future__ import annotations

import datetime
from typing import List

from pydantic import BaseModel, Field
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    select,
)
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import mapped_column

from db import Base, DbResult


class TransactionSchema(BaseModel):
    id: int = Field(exclude=False, title="id")
    name: str = Field(exclude=False, title="name")
    client_type: int = Field(exclude=False, title="client_type")
    price: float = Field(exclude=False, title="price")
    date: datetime.datetime = Field(exclude=False, title="date")
    bus_id: int = Field(exclude=False, title="bus_id")


# pylint: disable=E0213,C0115,C0116,W0718
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String)
    client_type = mapped_column(ForeignKey("client_types.id"))
    price = Column(Float)
    date = Column(DateTime)
    bus_id = mapped_column(ForeignKey("buses.id"))
   

    async def add(self, session: AsyncSession) -> DbResult:
        try:
            session.add(self)
            await session.commit()
            return DbResult.result(self.id)
        except Exception as e:
            await session.rollback()
            return DbResult.error(str(e), False)

    async def get_by_id(session: AsyncSession, transaction_id: int) -> DbResult:
        try:
            result = await session.execute(select(Transaction).where(Transaction.id == transaction_id))
            data = result.scalars().first()
            await session.commit()
            return DbResult.result(data)
        except Exception as e:
            return DbResult.error(str(e))
        
    async def get_by_bus_and_time(session: AsyncSession, bus_id: int,date_from: datetime.datetime, date_to: datetime.datetime) -> DbResult:
        try:
            result = await session.execute(select(Transaction).where(Transaction.bus_id == bus_id).where(Transaction.date >= date_from).where(Transaction.date <= date_to))
            data = result.scalars().all()
            await session.commit()
            return DbResult.result(data)
        except Exception as e:
            return DbResult.error(str(e))
        
    
    async def get_by_bus(session: AsyncSession, bus_id: int) -> DbResult:
        try:
            result = await session.execute(select(Transaction).where(Transaction.bus_id == bus_id))
            data = result.scalars().all()
            await session.commit()
            return DbResult.result(data)
        except Exception as e:
            return DbResult.error(str(e))
        
    async def get_all(session: AsyncSession) -> DbResult:
        try:
            result = await session.execute(select(Transaction))
            data = result.scalars().all()
            await session.commit()
            return DbResult.result(data)
        except Exception as e:
            return DbResult.error(str(e))

    async def get_by_date(session: AsyncSession,date_from: datetime.datetime, date_to: datetime.datetime) -> DbResult:
        try:
            result = await session.execute(select(Transaction).where(Transaction.date >= date_from).where(Transaction.date <= date_to))
            data = result.scalars().all()
            await session.commit()
            return DbResult.result(data)
        except Exception as e:
            return DbResult.error(str(e))
        

    async def get_by_client_type(session: AsyncSession, client_type: int) -> DbResult:
        try:
            result = await session.execute(select(Transaction).where(Transaction.client_type == client_type))
            data = result.scalars().all()
            await session.commit()
            return DbResult.result(data)
        except Exception as e:
            return DbResult.error(str(e))

    def from_one_to_schema(transaction: Transaction) -> TransactionSchema:
        try:
            transaction_schema = TransactionSchema(
                id=transaction.id,
                name=transaction.name,
                client_type = transaction.client_type,
                price = transaction.price,
                date=transaction.date,
                bus_id=transaction.bus_id
            )
            return transaction_schema
        except Exception:
            return None

    def from_list_to_schema(transactions: List[Transaction]) -> list[TransactionSchema]:
        try:
            return [Transaction.from_one_to_schema(b) for b in transactions]
        except Exception:
            return []


async def init_transaction(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)