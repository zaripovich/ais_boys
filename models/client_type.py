from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, insert, select, update
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from db import Base, DbResult


class ClientTypeSchema(BaseModel):
    id: int = Field(exclude=False, title="id")
    client_name: str = Field(exclude=False, title="client_name")
    discount: int = Field(exclude=False, title="discount")


# pylint: disable=E0213,C0115,C0116,W0718
class ClientType(Base):
    __tablename__ = "client_types"

    id = Column(Integer, autoincrement=True, primary_key=True)
    client_name = Column(String, unique=True)
    discount = Column(Integer)

    async def add(self, session: AsyncSession) -> DbResult:
        try:
            result = await session.execute(insert(ClientType).values((None,self.client_name,self.discount,)))
            if result.is_insert:
                await session.commit()
                return DbResult.result(self.id)
            else:
                raise "Error"
        except Exception as e:
            await session.rollback()
            return DbResult.error(str(e), False)
        
    async def set_discount(session: AsyncSession, client_type: int, new_discount: float) -> DbResult:
        try:
            await session.execute(update(ClientType).where(ClientType.id == client_type).values(discount=new_discount))
            await session.commit()
            return DbResult.result(True)
        except Exception as e:
            return DbResult.error(str(e),False)

    async def get_by_id(session: AsyncSession, client_type: int) -> DbResult:
        try:
            result = await session.execute(select(ClientType).where(ClientType.id == client_type))
            data = result.scalars().first()
            await session.commit()
            return DbResult.result(data)
        except Exception as e:
            return DbResult.error(str(e))

    async def get_all(session: AsyncSession) -> DbResult:
        try:
            result = await session.execute(select(ClientType))
            data = result.scalars().all()
            await session.commit()
            return DbResult.result(data)
        except Exception as e:
            return DbResult.error(str(e))

    def from_one_to_schema(client_type: ClientType) -> ClientTypeSchema:
        try:
            clienttype_schema = ClientTypeSchema(
                id=client_type.id,
                client_name=client_type.client_name,
                discount=client_type.discount,
            )
            return clienttype_schema
        except Exception:
            return None

    def from_list_to_schema(client_types: List[ClientType]) -> list[ClientTypeSchema]:
        try:
            return [ClientType.from_one_to_schema(b) for b in client_types]
        except Exception:
            return []


async def init_client_type(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
