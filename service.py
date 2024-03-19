import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi_async_sqlalchemy import SQLAlchemyMiddleware
from sqlalchemy.ext.asyncio import AsyncEngine

from db import engine
from models.bus import Bus, init_bus
from models.client_type import ClientType, init_client_type
from models.transaction import init_transaction
from routes.bus import init_bus_routes

# pylint: disable=E0401
from routes.client_type import init_client_types_routes
from routes.stats import init_stats_routes
from routes.transaction import init_transactions_routes

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)




app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_middleware(SQLAlchemyMiddleware, db_url=os.environ["DATABASE_URL"])


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Оплата проезда",
        version="2.5.0",
        summary="----------",
        description="Бэкэнд сервиса по оплате проезда",
        routes=app.routes,
    )
    return openapi_schema


async def init_models():
    try:
        if os.environ.get("REINIT_DB") == "1":
            await init_client_type(engine)
            await init_bus(engine)
            await init_transaction(engine)
            await init_base_vars(engine)
        print("Done\n")
    except Exception as e:
        print(e)

async def init_base_vars(engine: AsyncEngine):
    try:
        client_types = [
            ["Пенсионеры",30],
            ["Студенты",15],
            ["Обычные",0],
            ["Алга",10],
            ["Инвалиды",70],
        ]
        for client in client_types:
            client_temp = ClientType()
            client_temp.client_name = client[0]
            client_temp.discount = client[1]
            async with engine.connect() as conn:
                result = await client_temp.add(conn)
                if result.is_error:
                    print("Error create client_types\n")
        
        for bus in range(4):
            bus_temp = Bus()
            bus_temp.price = bus+30
            bus_temp.status = True
            async with engine.connect() as conn:
                result = await bus_temp.add_first(conn)
                if result.is_error:
                    print("Error create buses\n")

        print("Done\n")

    except Exception as e:
        print(e)


def run():
    init_client_types_routes(app)
    init_bus_routes(app)
    init_transactions_routes(app)
    init_stats_routes(app)
    app.openapi_schema = custom_openapi()
    uvicorn.run(app, host=os.environ.get("HOST"), port=int(os.environ.get("PORT")))
