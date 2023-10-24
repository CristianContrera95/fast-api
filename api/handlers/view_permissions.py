from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.auth import auth
from api.handlers.http_errors import handle_exception
from app.sqlserverdb import get_db
from core.role_core import get_role
from core.view_permissions_core import (
    delete_view_role,
    get_all_view_permissions_by,
    get_view_role_by_id,
    new_view_role,
    update_view_role,
)
from models import Account, ViewRole

router = APIRouter()


@router.get("/")
def get_all_allowed_views(
    db: Session = Depends(get_db),
    params: Optional[str] = None,
    current_account: Account = Depends(auth.get_current_account),
):
    view_users = get_all_view_permissions_by(db, role_id=current_account.role_id)

    return view_users


@router.get("/{view_role_id}")
def get_view_role_permission(
    view_role_id: int,
    db: Session = Depends(get_db),
    params: Optional[str] = None,
    current_account: Account = Depends(auth.get_current_account),
):
    view_users = get_view_role_by_id(db, view_role_id)
    if view_users.role_id == current_account.role_id:
        return {"error": f"current_account_id: {current_account.id} not valid"}
    if view_users is None:
        return {"error": f"view_users_id: {view_role_id} not valid"}
    return {"view_users": view_users}


@router.put("/{view_users_id}")
def update_view_role_permission(
    view_users_id: int,
    view_users: ViewRole,
    db: Session = Depends(get_db),
    current_account: Account = Depends(auth.get_current_account),
):
    role = get_role(db, current_account.role_id)
    if (role is not None) and (role.name == "admin"):
        result = update_view_role(db, view_users_id, view_users)
        if isinstance(result, str):
            return {"error": result}
        return {"view_users": result}
    return {"error": "current account don't have permission"}


@router.post("/")
def new_role_view(
    view_role: ViewRole, db: Session = Depends(get_db), current_account: Account = Depends(auth.get_current_account)
):
    try:
        permission_uid = new_view_role(db, view_role, current_account)
        return {"view_permission_id": permission_uid}
    except Exception as e:
        handle_exception(e)


@router.delete("/{view_role_id}")
def delete_role_view(
    view_role_id: int, db: Session = Depends(get_db), current_account: Account = Depends(auth.get_current_account)
):
    try:
        delete_view_role(db, view_role_id, current_account)
        return {"message": "View-Role permission deleted successfully."}
    except Exception as e:
        handle_exception(e)
