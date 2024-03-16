from typing import Optional

from fastapi import Depends, FastAPI, Response
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from db import DbResult, get_session
from models.client_type import ClientType, ClientTypeSchema


class NewValue(BaseModel):
    client_type: int = Field(exclude=False, title="client_type")
    new_discount: int = Field(exclude=False, title="new_discount")


# pylint: disable=E0213,C0115,C0116,W0718
class UpdateResponse(BaseModel):
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
class ClientTypeResponse(BaseModel):
    code: int = Field(exclude=False, title="code")
    error_desc: Optional[str] = Field(exclude=False, title="description")
    value: Optional[ClientTypeSchema] = Field(exclude=False, title="value")

    def __init__(
        self,
        code: int = 200,
        error_desc: Optional[str] = None,
        value: Optional[ClientTypeSchema] = None,
    ):
        super().__init__(code=code, error_desc=error_desc, value=value)


# pylint: disable=E0213,C0115,C0116,W0718
class ClientTypesResponse(BaseModel):
    code: int = Field(exclude=False, title="code")
    error_desc: Optional[str] = Field(exclude=False, title="description")
    value: Optional[list[ClientTypeSchema]] = Field(exclude=False, title="values",serialization_alias="values")

    def __init__(
        self,
        code: int = 200,
        error_desc: Optional[str] = None,
        value: Optional[list[ClientTypeSchema]] = [],
    ):
        super().__init__(code=code, error_desc=error_desc, value=value)


def init_client_types_routes(app: FastAPI):


    @app.get("/client_types/get_by_id/{id}", response_model=ClientTypeResponse)
    async def get_by_id(
        response: Response,
        id: int,
        session: AsyncSession = Depends(get_session),
    ):
        try:
            result: DbResult = await ClientType.get_by_id(session, id)
            if result.is_error is True:
                response.status_code = 500
                return ClientTypeResponse(code=500, error_desc=result.error_desc)
            return ClientTypeResponse(code=200, value=ClientType.from_one_to_schema(result.value))
        except Exception as e:
            response.status_code = 500
            return ClientTypeResponse(code=500, error_desc=str(e))
        
    

    @app.get("/client_types/get_all", response_model=ClientTypesResponse)
    async def get_all(
        response: Response,
        session: AsyncSession = Depends(get_session),
    ):
        try:
            result: DbResult = await ClientType.get_all(session)
            if result.is_error is True:
                response.status_code = 500
                return ClientTypesResponse(code=500, error_desc=result.error_desc)
            return ClientTypesResponse(code=200, value=ClientType.from_list_to_schema(result.value))
        except Exception as e:
            response.status_code = 500
            return ClientTypesResponse(code=500, error_desc=str(e))
        

    
    @app.put("/client_types/update_discount", response_model=UpdateResponse)
    async def update_discount(
        response: Response,
        data: NewValue,
        session: AsyncSession = Depends(get_session),
    ):
        try:
            fuel_result = await ClientType.get_by_id(session,data.client_type)
            if fuel_result.is_error:
                response.status_code = 500
                return UpdateResponse(code=500, error_desc="Client Not Found")
            result = await ClientType.set_discount(session,data.client_type,data.new_discount)
            if result is False:
                response.status_code = 500
                return UpdateResponse(code=500, error_desc=result.error_desc)
            return UpdateResponse(code=200, value=True)
        except Exception as e:
            response.status_code = 500
            return ClientTypesResponse(code=500, error_desc=str(e))
        
    

    
