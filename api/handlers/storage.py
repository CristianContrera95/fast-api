from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.auth import auth
from api.handlers.http_errors import handle_exception
from app.sqlserverdb import get_db
from core import storage_core
from models.account_model import Account

router = APIRouter()


@router.get("/token")
def get_temp_token(
    db: Session = Depends(get_db),
    params: Optional[str] = None,
    current_account: Account = Depends(auth.get_current_account),
):
    try:
        token, account_name, container_name, cloud_name = storage_core.get_temp_token(db, current_account)
        return {
            "token": token,
            "account_name": account_name,
            "container_name": container_name,
            "cloud_name": cloud_name,
        }
    except Exception as e:
        handle_exception(e)
