
import datetime
from typing import Optional

from fastapi import Depends, FastAPI, Response
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from db import DbResult, get_session
from models.transaction import Transaction


# pylint: disable=E0213,C0115,C0116,W0718
class StatsResponse(BaseModel):
    code: int = Field(exclude=False, title="code")
    error_desc: Optional[str] = Field(exclude=False, title="description")
    value: Optional[float] = Field(exclude=False, title="value")

    def __init__(
        self,
        code: int = 200,
        error_desc: Optional[str] = None,
        value: Optional[float] = None,
    ):
        super().__init__(code=code, error_desc=error_desc, value=value)


class BusDateFilter(BaseModel):
    bus_id: int = Field(exclude=False, title="bus_id"),
    date_from: datetime.datetime = Field(exclude=False, title="date_from"),
    date_to: datetime.datetime = Field(exclude=False, title="date_to"),



def init_stats_routes(app: FastAPI):


    @app.post("/stats/get_all_price", response_model=StatsResponse)
    async def get_all_price(
        response: Response,
        data: BusDateFilter,
        session: AsyncSession = Depends(get_session),
    ):
        try:
            result_trans: DbResult = await Transaction.get_by_bus_and_time(session,data.bus_id,data.date_from,data.date_to)
            if result_trans.is_error is True:
                response.status_code = 500
                return StatsResponse(code=500, error_desc=result_trans.error_desc)
            transactions: list[Transaction] = result_trans.value
            price = 0.0
            for transaction in transactions:
                price += transaction.price
            return StatsResponse(code=200, value=price)
        except Exception as e:
            response.status_code = 500
            return StatsResponse(code=500, error_desc=str(e))
        
    
    @app.get("/stats/get_median_price/{id}", response_model=StatsResponse)
    async def get_median_price(
        response: Response,
        id: int,
        session: AsyncSession = Depends(get_session),
    ):
        try:
            result_trans: DbResult = await Transaction.get_by_bus(session,id)
            if result_trans.is_error is True:
                response.status_code = 500
                return StatsResponse(code=500, error_desc=result_trans.error_desc)
            transactions: list[Transaction] = result_trans.value
            price = 0.0
            for transaction in transactions:
                price += transaction.price
            if len(transactions):
                price /= len(transactions)
            return StatsResponse(code=200, value=price)
        except Exception as e:
            response.status_code = 500
            return StatsResponse(code=500, error_desc=str(e))
        
        
    @app.post("/stats/get_human_count", response_model=StatsResponse)
    async def get_human_count(
        response: Response,
        data: BusDateFilter,
        session: AsyncSession = Depends(get_session),
    ):
        try:
            result_trans: DbResult = await Transaction.get_by_bus_and_time(session,data.bus_id,data.date_from,data.date_to)
            if result_trans.is_error is True:
                response.status_code = 500
                return StatsResponse(code=500, error_desc=result_trans.error_desc)
            transactions: list[Transaction] = result_trans.value
            date = data.date_to - data.date_from
            power = len(transactions)/(date.total_seconds()/60/60)
            return StatsResponse(code=200, value=power)
        except Exception as e:
            response.status_code = 500
            return StatsResponse(code=500, error_desc=str(e))   
