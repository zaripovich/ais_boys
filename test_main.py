import datetime
import json
import os
import random as rnd

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from fastapi.testclient import TestClient
from fastapi_async_sqlalchemy import SQLAlchemyMiddleware

from routes.bus import init_bus_routes
from routes.client_type import init_client_types_routes
from routes.stats import init_stats_routes
from routes.transaction import init_transactions_routes

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
app.add_middleware(SQLAlchemyMiddleware, db_url=os.environ["DATABASE_URL"])

init_client_types_routes(app)
init_bus_routes(app)
init_transactions_routes(app)
init_stats_routes(app)


client = TestClient(app)
auth = ""


def test_add_bus():
    test_data = {"price": 35}
    post_data = json.dumps(test_data)
    response = client.post("/bus/add", data=post_data)
    print(response.json())
    assert response.json()["code"] == 200
    assert response.json()["value"] is not None

def test_get_all_bus():
    response = client.get("/bus/get_all")
    print(response.json())
    assert response.json()["code"] == 200
    assert response.json()["values"] is not None


def test_get_bus_by_id():
    response = client.get("/bus/get_by_id/1")
    print(response.json())
    assert response.json()["code"] == 200
    assert response.json()["value"] is not None



def test_get_all_client_types():
    response = client.get("/client_types/get_all")
    print(response.json())
    assert response.json()["code"] == 200
    assert response.json()["values"] is not None


def test_get_client_type_by_id():
    response = client.get("/client_types/get_by_id/1")
    print(response.json())
    assert response.json()["code"] == 200
    assert response.json()["value"] is not None


def test_update_client_discount():
    response = client.get("/client_types/get_by_id/1")
    print(response.json())
    assert response.json()["code"] == 200
    assert response.json()["value"] is not None
    response.json()["value"]["discount"]
    new_discount = rnd.randint(30, 40)
    test_data = {"client_type": 1, "new_discount": new_discount}
    post_data = json.dumps(test_data)
    response_2 = client.put("/client_types/update_discount", data=post_data)
    assert response_2.json()["code"] == 200
    assert response_2.json()["value"] == 1
    response_3 = client.get("/client_types/get_by_id/1")
    print(response_3.json())
    assert response_3.json()["code"] == 200
    assert response_3.json()["value"] is not None
    new_discount_result = response_3.json()["value"]["discount"]
    assert new_discount_result == new_discount




def test_transactions_add():
    test_data = {"name": "125XFS", "client_type": 1, "bus_id": 1}
    post_data = json.dumps(test_data)
    response = client.post(
        "/transactions/add", data=post_data
    )
    assert response.json()["code"] == 200
    assert response.json()["value"] is not None


def test_transaction_get_by_id():
    response = client.get(
        "/transactions/get_by_id/1"
    )
    assert response.json()["code"] == 200
    assert response.json()["value"] is not None


def test_get_all_transactions():
    response = client.get(
        "/transactions/get_all"
    )
    assert response.json()["code"] == 200
    assert response.json()["values"] is not None


def test_get_median_price():
    response = client.get(
        "/stats/get_median_price/1"
    )
    print(response.json())
    assert response.json()["code"] == 200
    assert response.json()["value"] is not None


def test_get_all_price():
    test_data = {"bus_id": 1, "date_from": datetime.datetime(day=8,month=3,year=2024).isoformat(), "date_to": datetime.datetime.now().isoformat()}
    post_data = json.dumps(test_data)
    response = client.post(
        "/stats/get_all_price", data= post_data
    )
    print(response.json())
    assert response.json()["code"] == 200
    assert response.json()["value"] is not None


