from typing import Optional

from fastapi import Depends, FastAPI, Response
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from db import DbResult, get_session
from models.bus import Bus, BusSchema


class NewBus(BaseModel):
    price: int = Field(exclude=False, title="price")


# pylint: disable=E0213,C0115,C0116,W0718
class AddResponse(BaseModel):
    code: int = Field(exclude=False, title="code")
    error_desc: Optional[str] = Field(exclude=False, title="description")
    value: Optional[int] = Field(exclude=False, title="value")

    def __init__(
        self, code: int = 200, error_desc: Optional[str] = "", value: Optional[int] = None
    ):
        super().__init__(code=code, error_desc=error_desc, value=value)


# pylint: disable=E0213,C0115,C0116,W0718
class DeleteResponse(BaseModel):
    code: int = Field(exclude=False, title="code")
    error_desc: Optional[str] = Field(exclude=False, title="description")
    value: Optional[bool] = Field(exclude=False, title="value")

    def __init__(
        self,
        code: int = 200,
        error_desc: Optional[str] = None,
        value: Optional[bool] = True,
    ):
        super().__init__(code=code, error_desc=error_desc, value=value)


# pylint: disable=E0213,C0115,C0116,W0718
class BusResponse(BaseModel):
    code: int = Field(exclude=False, title="code")
    error_desc: Optional[str] = Field(exclude=False, title="description")
    value: Optional[BusSchema] = Field(exclude=False, title="value")

    def __init__(
        self,
        code: int = 200,
        error_desc: Optional[str] = None,
        value: Optional[BusSchema] = None,
    ):
        super().__init__(code=code, error_desc=error_desc, value=value)


# pylint: disable=E0213,C0115,C0116,W0718
class BusesResponse(BaseModel):
    code: int = Field(exclude=False, title="code")
    error_desc: Optional[str] = Field(exclude=False, title="description")
    value: Optional[list[BusSchema]] = Field(exclude=False, title="values",serialization_alias="values")

    def __init__(
        self,
        code: int = 200,
        error_desc: Optional[str] = None,
        value: Optional[list[BusSchema]] = [],
    ):
        super().__init__(code=code, error_desc=error_desc, value=value)


def init_bus_routes(app: FastAPI):

    @app.post(
        "/bus/add", response_model=AddResponse, response_model_exclude_none=True
    )
    async def add(
        response: Response,
        data: NewBus,
        session: AsyncSession = Depends(get_session),
    ):
        try:
            
            new_bus = Bus()
            new_bus.price = data.price
            new_bus.status = True
            result = await new_bus.add(session)
            if result.is_error is True:
                response.status_code = 500
                return AddResponse(code=500, error_desc=result.error_desc)
            return AddResponse(code=200, value=result.value)
        except Exception as e:
            response.status_code = 500
            return AddResponse(code=500, error_desc=str(e))

    @app.get("/bus/get_by_id/{id}", response_model=BusResponse)
    async def get_by_id(
        response: Response,
        id: int,
        session: AsyncSession = Depends(get_session),
    ):
        try:
            result: DbResult = await Bus.get_by_id(session, id)
            if result.is_error is True:
                response.status_code = 500
                return BusResponse(code=500, error_desc=result.error_desc)
            return BusResponse(code=200, value=Bus.from_one_to_schema(result.value))
        except Exception as e:
            response.status_code = 500
            return BusResponse(code=500, error_desc=str(e))
        
    

    @app.get("/bus/get_all", response_model=BusesResponse)
    async def get_all(
        response: Response,
        session: AsyncSession = Depends(get_session),
    ):
        try:
            result: DbResult = await Bus.get_all(session)
            if result.is_error is True:
                response.status_code = 500
                return BusesResponse(code=500, error_desc=result.error_desc)
            return BusesResponse(code=200, value=Bus.from_list_to_schema(result.value))
        except Exception as e:
            response.status_code = 500
            return BusesResponse(code=500, error_desc=str(e))


    @app.delete("/bus/{id}", response_model=DeleteResponse)
    async def delete(
        response: Response,
        id: int,
        session: AsyncSession = Depends(get_session),
    ):
        try:
            result = await Bus.delete(session, id)
            if result is False:
                response.status_code = 500
                return DeleteResponse(code=500, error_desc=result.error_desc)
            return DeleteResponse(code=200, value=result.value)
        except Exception as e:
            response.status_code = 500
            return DeleteResponse(code=500, error_desc=str(e))