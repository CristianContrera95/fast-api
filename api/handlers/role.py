from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.auth import auth
from app.sqlserverdb import get_db
from core.role_core import delete_role, get_all_roles, get_role, new_role
from models import RoleBase
from models.account_model import Account

router = APIRouter()


@router.get("/")  # , response_model=List[RoleModel]
def get_all_role_view(
    db: Session = Depends(get_db),
    params: Optional[str] = None,
    current_account: Account = Depends(auth.get_current_account),
):
    all_role = get_all_roles(db)
    return {"roles": all_role}


@router.get("/{role_id}")
def get_role_view(
    role_id: int,
    db: Session = Depends(get_db),
    params: Optional[str] = None,
    current_account: Account = Depends(auth.get_current_account),
):
    role = get_role(db, role_id)
    if role is None:
        return {"error": f"role_id: {role_id} not valid"}
    return {"role": role}


@router.post("/")
def new_role_view(
    role_model: RoleBase, db: Session = Depends(get_db), current_account: Account = Depends(auth.get_current_account)
):
    result = new_role(db, role_model)
    if isinstance(result, str):
        return {"error": result}
    return {"role_id": result}


@router.delete("/{role_id}")
def delete_role_view(
    role_id: int, db: Session = Depends(get_db), current_account: Account = Depends(auth.get_current_account)
):
    result = delete_role(db, role_id)
    if isinstance(result, str):
        return {"error": result}
    return {"role": f"deleted {result} rows"}
