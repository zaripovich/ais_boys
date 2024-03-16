import datetime
import threading
from typing import Optional

from fastapi import Depends, FastAPI, Response
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from db import DbResult, get_session
from models.bus import Bus
from models.client_type import ClientType
from models.transaction import Transaction, TransactionSchema


class NewTransaction(BaseModel):
    name: str = Field(exclude=False, title="name")
    client_type: int = Field(exclude=False, title="client_type")
    bus_id: int = Field(exclude=False, title="bus_id")

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
class TransactionResponse(BaseModel):
    code: int = Field(exclude=False, title="code")
    error_desc: Optional[str] = Field(exclude=False, title="description")
    value: Optional[TransactionSchema] = Field(exclude=False, title="value")

    def __init__(
        self,
        code: int = 200,
        error_desc: Optional[str] = None,
        value: Optional[TransactionSchema] = None,
    ):
        super().__init__(code=code, error_desc=error_desc, value=value)


# pylint: disable=E0213,C0115,C0116,W0718
class TransactionsResponse(BaseModel):
    code: int = Field(exclude=False, title="code")
    error_desc: Optional[str] = Field(exclude=False, title="description")
    value: Optional[list[TransactionSchema]] = Field(exclude=False, title="values",serialization_alias="values")

    def __init__(
        self,
        code: int = 200,
        error_desc: Optional[str] = None,
        value: Optional[list[TransactionSchema]] = [],
    ):
        super().__init__(code=code, error_desc=error_desc, value=value)


def init_transactions_routes(app: FastAPI):
    @app.post(
        "/transactions/add", response_model=AddResponse, response_model_exclude_none=True
    )
    async def add(
        response: Response,
        data: NewTransaction,
        session: AsyncSession = Depends(get_session),
    ):
        try:            
            bus_result = await Bus.get_by_id(session,data.bus_id)
            if not bus_result.is_error:

                if bus_result.value.status is False:
                    response.status_code = 502
                    return AddResponse(code=502, error_desc="Bus status is false")
                

            client_result = await ClientType.get_by_id(session,data.client_type)
            if client_result.is_error:
                response.status_code = 500
                return AddResponse(code=500, error_desc="Client Not Found")
            
            new_transaction = Transaction()
            new_transaction.name = data.name
            new_transaction.client_type = data.client_type
            new_transaction.price = bus_result.value.price * (100-client_result.value.discount)/100
            new_transaction.date = datetime.datetime.now()
            new_transaction.bus_id = data.bus_id
            result = await new_transaction.add(session)
            if result.is_error is True:
                response.status_code = 500
                return AddResponse(code=500, error_desc=result.error_desc)


            await Bus.set_active(session,new_transaction.bus_id,False)

        
            thread = threading.Thread(target=Bus.auto_open,args=(session,data.bus_id,))
            thread.start()
            return AddResponse(code=200, value=result.value)
        except Exception as e:
            response.status_code = 500
            return AddResponse(code=500, error_desc=str(e))

    @app.get("/transactions/get_by_id/{id}", response_model=TransactionResponse)
    async def get_by_id(
        response: Response,
        id: int,
        session: AsyncSession = Depends(get_session),
    ):
        try:
            result: DbResult = await Transaction.get_by_id(session, id)
            if result.is_error is True:
                response.status_code = 500
                return TransactionResponse(code=500, error_desc=result.error_desc)
            return TransactionResponse(code=200, value=Transaction.from_one_to_schema(result.value))
        except Exception as e:
            response.status_code = 500
            return TransactionResponse(code=500, error_desc=str(e))

    @app.get("/transactions/get_by_fuel/{id}", response_model=TransactionResponse)
    async def get_by_fuel_type(
        response: Response,
        id: int,
        session: AsyncSession = Depends(get_session),
    ):
        try:
            result: DbResult = await Transaction.get_by_id(session, id)
            if result.is_error is True:
                response.status_code = 500
                return TransactionResponse(code=500, error_desc=result.error_desc)
            return TransactionResponse(code=200, value=Transaction.from_one_to_schema(result.value))
        except Exception as e:
            response.status_code = 500
            return TransactionResponse(code=500, error_desc=str(e))


    @app.get("/transactions/get_all", response_model=TransactionsResponse)
    async def get_all(
        response: Response,
        session: AsyncSession = Depends(get_session),
    ):
        try:
            result: DbResult = await Transaction.get_all(session)
            if result.is_error is True:
                response.status_code = 500
                return TransactionsResponse(code=500, error_desc=result.error_desc)
            result.value.reverse()
            return TransactionsResponse(code=200, value=Transaction.from_list_to_schema(result.value))
        except Exception as e:
            response.status_code = 500
            return TransactionsResponse(code=500, error_desc=str(e))
