from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.auth import auth
from app import logger
from app.sqlserverdb import get_db
from core.account_core import delete_account, get_account, get_all_account, new_account, update_account
from models.account_model import Account

router = APIRouter()


@router.get("/")
def get_all_account_view(db: Session = Depends(get_db), params: Optional[str] = None):
    logger.info(params)
    all_account = get_all_account(db)
    if isinstance(all_account, str):
        return {"error": "account not found"}
    return {"account": all_account}


@router.get("/{account_uid}")
def get_account_view(account_uid: str, db: Session = Depends(get_db), params: Optional[str] = None):
    account = get_account(db, account_uid)
    if isinstance(account, str):
        return {"error": "account_id not valid"}
    else:
        return {"account": account}


@router.post("/")
def new_account_view(account: Account, db: Session = Depends(get_db)):
    logger.info(account)
    try:
        result = new_account(db, account)
        return {"account_id": result}
    except Exception as e:  # TODO: This is still suboptimal, creating custom exceptions would be ideal.
        return {"error": str(e)}


@router.put("/{account_uid}")
def update_account_view(
    account_uid: str,
    account: Account,
    db: Session = Depends(get_db),
    current_account: Account = Depends(auth.get_current_account),
):
    logger.info(account_uid)
    logger.info(account)
    try:
        result = update_account(db, account_uid, account)
        return {"account": result}
    except Exception as e:  # TODO: This is still suboptimal, creating custom exceptions would be ideal.
        return {"error": str(e)}


@router.delete("/{account_uid}")
def delete_account_view(
    account_uid: str, db: Session = Depends(get_db), current_account: Account = Depends(auth.get_current_account)
):
    result = delete_account(db, account_uid)
    if isinstance(result, str):
        return {"error": result}
    return {"account": f"deleted {result} rows"}
