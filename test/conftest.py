import json
import os
from test.api.auth_helper import login
from typing import Generator
from urllib.parse import quote_plus

import pytest
from bson import ObjectId
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app import mongodb
from app.sqlserverdb import Base, get_db

__SQL_DATABASE_NAME = os.getenv("SQL_DATABASE")
__MONGO_DATABASE_NAME = os.getenv("DATABASE_NAME")

__URI = (
    f'DRIVER={os.getenv("SQL_DRIVER")};'
    + f'SERVER={os.getenv("SQL_SERVER")};'
    + f"DATABASE={__SQL_DATABASE_NAME};"
    + f'UID={os.getenv("SQL_USER")};'
    + f'PWD={os.getenv("SQL_PASS")}'
)

__PARAMS = quote_plus(__URI)
__SQLALCHEMY_TEST_DATABASE_URI = "mssql+pyodbc:///?odbc_connect=%s" % __PARAMS

print(__SQLALCHEMY_TEST_DATABASE_URI)
engine = create_engine(__SQLALCHEMY_TEST_DATABASE_URI, connect_args={"check_same_thread": False})
mongo_instance = mongodb.mongo_class()

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

__TEST_SQL_DATA_PATH = "./test/test_data/test_data.sql"
__TEST_MONGO_DATA_PATH = "./test/test_data/test_data.json"


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True, scope="session")
def db_setup() -> Generator:
    print("SETTING DATABASE UP")
    mongo_instance.myclient.drop_database(__MONGO_DATABASE_NAME)
    run_inserts()
    yield


def run_inserts():
    json_file = open(__TEST_MONGO_DATA_PATH)
    data = json.load(json_file)
    for ed in data["edge_devices"]:
        ed["_id"] = ObjectId(ed["_id"])
    mongo_instance.mydb["edge_devices"].insert_many(data["edge_devices"])
    from main import app

    app.dependency_overrides[get_db] = override_get_db
    sql_file = open(__TEST_SQL_DATA_PATH)
    escaped_sql = text(sql_file.read())
    engine.execute(escaped_sql)


@pytest.fixture(scope="session")
def sql_db(db_setup) -> Generator:  # TODO: Avoid this code repetition.
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def mongo_db(db_setup) -> Generator:
    yield mongo_instance


@pytest.fixture(scope="session")
def client(db_setup) -> Generator:
    print("INITIALIZING CLIENT")
    from main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def login_token(client: TestClient):
    return login(client)


@pytest.fixture(scope="session")
def headers(login_token: str):
    headers = {"Host": "localhost", "Authorization": f"Bearer {login_token}"}

    return headers
