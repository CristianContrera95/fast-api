from typing import Optional

from bson.objectid import ObjectId
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.auth import auth
from app.sqlserverdb import get_db
from core import edge_device_core
from models import edge_device_model
from models.account_model import Account

router = APIRouter()


@router.get("/")
def get_all_edge_device(params: Optional[str] = None, current_account: Account = Depends(auth.get_current_account)):
    all_edge_devices = edge_device_core.get_all_edge_device()
    return {"edge_devices": all_edge_devices}


@router.get("/{edge_device_id}")
def get_edge_device(
    edge_device_id: str,
    db: Session = Depends(get_db),
    params: Optional[str] = None,
    current_account: Account = Depends(auth.get_current_account),
):
    if ObjectId.is_valid(edge_device_id):
        one_edge_device = edge_device_core.get_edge_device(db, edge_device_id)
        return {"edge_device": one_edge_device}
    else:
        return {"edge_device": "edge_device_id not valid"}


@router.post("/")
def new_edge_device(
    edge_device: edge_device_model.EdgeDevice,
    db: Session = Depends(get_db),
    current_account: Account = Depends(auth.get_current_account),
):
    new_edge_device = edge_device_core.new_edge_device(db, edge_device)
    return {"edge_device": new_edge_device}


@router.put("/{edge_device_id}")
def update_edge_device(
    edge_device_id: str,
    edge_device: edge_device_model.EdgeDevice,
    db: Session = Depends(get_db),
    current_account: Account = Depends(auth.get_current_account),
):
    if ObjectId.is_valid(edge_device_id):
        update_edge_device = edge_device_core.update_edge_device(db, edge_device_id, edge_device)
        return {"edge_device": update_edge_device}
    else:
        return {"edge_device": "edge_device_id not valid"}


@router.delete("/{edge_device_id}")
def delete_edge_device(edge_device_id: str, current_account: Account = Depends(auth.get_current_account)):
    if ObjectId.is_valid(edge_device_id):
        deleted_edge_device = edge_device_core.delete_edge_device(edge_device_id)
        return {"edge_device": deleted_edge_device}
    else:
        return {"edge_device": "edge_device_id not valid"}


@router.post("/{edge_device_id}/send_status")
def send_status(
    edge_device_id: str, db: Session = Depends(get_db), current_account: Account = Depends(auth.get_current_account)
):
    if ObjectId.is_valid(edge_device_id):
        edge_device = edge_device_core.send_status(db, edge_device_id)
        return {"edge_device": edge_device}
    else:
        return {"edge_device": "edge_device_id not valid"}
