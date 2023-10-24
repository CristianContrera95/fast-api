import logging
import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

import app
from app import oauth2_scheme
from app.sqlserverdb import get_db
from core.exceptions.cloud_service_exceptions import CloudCredentialsException
from core.exceptions.entity_not_found_exceptions import CloudServiceNotFoundException
from core.storage_core import ContainerType, get_temp_token
from db.sql import account_sql, edge_device_sql
from models.account_model import Account

logger = logging.getLogger(__name__)
API_CLIENT_ID = os.environ["API_CLIENT_ID"]
API_CLIENT_SECRET = os.environ["API_CLIENT_SECRET"]

router = APIRouter()


# User's authentication.


class Token(BaseModel):
    access_token: str
    token_type: str
    sas_token: Optional[str]


class TokenData(BaseModel):
    username: Optional[str] = None


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, password):
    return pwd_context.verify(plain_password, password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_account(db, username: str):
    account = account_sql.get_account_by_username(db, username)
    if not account:
        return False
    return account


def get_edge_device(db, id: str):
    edge_device = edge_device_sql.get_edge_device_by_id(db, id)
    if not edge_device:
        return False
    return edge_device


def authenticate_account(db: Session, email: str, password: str):
    account = account_sql.get_account_by_email(db, email)
    if not account:
        return False
    if not verify_password(password, account.password):
        return False
    return account


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=app.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, app.SECRET_KEY, algorithm=app.ALGORITHM)
    return encoded_jwt


async def get_current_account(token: str = Depends(app.oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, app.SECRET_KEY, algorithms=[app.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    account = get_account(db, username=token_data.username)
    if account is None:
        raise credentials_exception
    return account


async def get_current_active_account(current_account: Account = Depends(get_current_account)):
    if current_account.disabled:
        raise HTTPException(status_code=400, detail="Inactive account")
    return current_account


@router.post("/token", response_model=Token)
async def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    """OAuth2PasswordRequestForm requires username field, this represent email field in front panel"""
    account = authenticate_account(db, form_data.username, form_data.password)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=app.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": account.username}, expires_delta=access_token_expires)

    sas_token = None
    try:
        sas_token, _, _, _ = get_temp_token(
            db,
            account,
            expiration=datetime.utcnow()
                       + timedelta(minutes=app.ACCESS_TOKEN_EXPIRE_MINUTES),  # Token for displaying frames
            container_name=ContainerType.ALERT_CONTAINER,
        )
    except CloudCredentialsException or CloudServiceNotFoundException as e:
        logger.error(str(e))

    return {"access_token": access_token, "token_type": "bearer", "sas_token": sas_token}


@router.get("/actual_token")
async def read_items(token: str = Depends(oauth2_scheme)):
    return {"token": token}


@router.get("/actual_account")
async def read_accounts_me(current_account: Account = Depends(get_current_account)):
    return current_account


# APIs' authentication.


def validate_api_client_id(
        x_client_id: str = Header(None), x_client_secret: str = Header(None), db: Session = Depends(get_db)
):
    if x_client_id == API_CLIENT_ID:
        validate_worker(x_client_id, x_client_secret)
    else:
        validate_edge_device(x_client_id, x_client_secret, db)


# Worker clients validation
def validate_worker(
        x_client_id: str = Header(None), x_client_secret: str = Header(None)
):  # TODO Improve with workers db registry
    if x_client_id != API_CLIENT_ID or x_client_secret != API_CLIENT_SECRET:
        logger.info(f"Worker of id {x_client_id} has reported wrong credentials, secret: {x_client_secret}.")
        __raise_auth_error()

    return x_client_id


# Edge device clients validation
def validate_edge_device(
        x_client_id: str = Header(None), x_client_secret: str = Header(None), db: Session = Depends(get_db)
):
    # X-Client-ID contains the edge device ID.
    edge_device = get_edge_device(db, x_client_id)

    if not edge_device:
        logger.info(f"Edge device of id {x_client_id} not found.")
        __raise_auth_error()

    secret = os.environ["API_CLIENT_SECRET"]
    if x_client_secret != secret:
        logger.info(f"Invalid secret {x_client_secret} for edge device {x_client_id}.")
        __raise_auth_error()

    return edge_device


def __raise_auth_error():
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate api credentials",
        headers={"WWW-Authenticate": "X-Client-ID"},
    )
