from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.auth import auth
from api.handlers.http_errors import handle_exception
from app.sqlserverdb import get_db
from core import view_core
from models.account_model import Account
from models.view_model import View

router = APIRouter()


@router.get("/{view_id}")
def generate_view(
    view_id: str, db: Session = Depends(get_db), current_account: Account = Depends(auth.get_current_account)
):
    try:
        component_view = view_core.generate_view(db, view_id, current_account)
        return {"component": component_view}
    except Exception as e:
        handle_exception(e)


@router.post("/")
def create_view(
    view: View, db: Session = Depends(get_db), current_account: Account = Depends(auth.get_current_account)
):
    created_view, errors = view_core.new_view(db, view)
    result = {"view": created_view}
    if errors:
        result["error"] = errors
    return result
