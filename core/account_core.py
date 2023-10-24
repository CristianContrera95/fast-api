from uuid import uuid4

from bcrypt import checkpw, gensalt, hashpw
from sqlalchemy.orm import Session

from app import logger
from db.sql.account_sql import get_account_by_email, get_account_by_username
from db.sql.utils import create_record, delete_record_by_id, get_record_by_id, get_records, update_record_by_id
from models import Account
from schemas import AccountSchema


def get_all_account(db: Session, skip: int = 0, limit: int = 100):
    accounts = get_records(db, skip, limit, AccountSchema)
    if accounts is None:
        logger.error("error, accounts not found")
        return "error, accounts not found"
    return accounts


def get_account(db: Session, account_id: str = "", account_username: str = "", account_email: str = ""):
    account = None
    if account_id:
        account = get_record_by_id(db, account_id, AccountSchema)
    elif account_username:
        account = get_account_by_username(db, account_username)
    elif account_username:
        account = get_account_by_email(db, account_email)

    if account is None:
        logger.error("error, account not found")
        return "error, account not found"
    return account


def __check_unique(db: Session, account: AccountSchema):
    logger.info(get_account_by_username(db, account.username))
    logger.info(get_account_by_email(db, account.email))
    account = get_account_by_username(db, account.username) or get_account_by_email(db, account.email)
    return not bool(account)


def __hashed_password(password):
    password_hash = password
    hashed = hashpw(password_hash.encode(), gensalt())
    return hashed.decode()


def __compare_hashed(password, hashed):
    return bool(checkpw(password.encode(), hashed.encode()))


def new_account(db: Session, account: Account):
    account_schema = AccountSchema(**account.dict(exclude_unset=True))
    if __check_unique(db, account_schema):
        account_schema.id = uuid4()
        account_schema.password = __hashed_password(account_schema.password)
        account_id = create_record(db, account_schema)
        if account_id == 0:
            raise Exception("error, can't add account")
        return account_id
    else:
        return "error, account username or email already exists"


def update_account(db: Session, account_id: str, account: Account):
    account_data = account.dict(exclude_unset=True)
    if "password" in account_data:
        account_data["password"] = __hashed_password(account_data["password"])
    updated_account = update_record_by_id(db, account_id, account_data, AccountSchema)
    if updated_account is None:
        raise Exception(f"error, account {account_id} don't exists")
    return updated_account


def delete_account(
    db: Session,
    account_id: str,
):
    result = delete_record_by_id(db, account_id, AccountSchema)
    if result is None:
        return f"error, account_id: {account_id} don't exists"
    return result
