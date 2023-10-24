import logging
import os
from time import sleep
from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.query import Query as _Query


class RetryingQuery(_Query):
    __max_retry_count__ = 3
    __sleep_time__ = 2

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __iter__(self):
        attempts = 0
        while True:
            attempts += 1
            try:
                return super().__iter__()
            except OperationalError as ex:
                if attempts > self.__max_retry_count__:
                    raise DataAccessException(str(ex))
                logging.error(
                    "! Database connection error: retrying Strategy => sleeping for {}s"
                    " and will retry (attempt #{} of {}) \n Detailed query impacted: {}".format(
                        self.__sleep_time__, attempts, self.__max_retry_count__, ex
                    )
                )
                sleep(self.__sleep_time__)
                continue

            # except StatementError as ex:
            #     error_message = f"Statement error, rolling back {str(ex)}"
            #     logging.error(error_message)
            #     self.session.rollback()
            #     continue


class DataAccessException(Exception):
    def __init__(self, message="An error ocurred while accessing database"):
        super().__init__(message)


__URI = (
    f'DRIVER={os.getenv("SQL_DRIVER")};'
    + f'SERVER={os.getenv("SQL_SERVER")};'
    + f'DATABASE={os.getenv("SQL_DATABASE")};'
    + f'UID={os.getenv("SQL_USER")};'
    + f'PWD={os.getenv("SQL_PASS")}'
)

__PARAMS = quote_plus(__URI)
__SQLALCHEMY_DATABASE_URI = "mssql+pyodbc:///?odbc_connect=%s" % __PARAMS

engine = create_engine(__SQLALCHEMY_DATABASE_URI)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, query_cls=RetryingQuery)

Base = declarative_base()


def get_db():
    db = None
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
