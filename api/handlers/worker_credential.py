from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.sqlserverdb import get_db
from core.worker_core import (
    delete_worker_credential,
    get_all_worker_credentials,
    new_worker_credential,
    update_worker_credential,
)
from models import WorkerCredential

router = APIRouter()


@router.get("/")
def get_all_worker_credentials_view(
    db: Session = Depends(get_db), worker_storage_id: int = 0, params: Optional[str] = None
):
    all_worker_credentials = get_all_worker_credentials(db, worker_storage_id)
    if isinstance(all_worker_credentials, str):
        return {"error": "worker_credentials not found"}
    return {"worker_credentials": all_worker_credentials}


@router.post("/")
def new_worker_credential_view(worker_credential: WorkerCredential, db: Session = Depends(get_db)):
    result = new_worker_credential(db, worker_credential)
    if isinstance(result, str):
        return {"error": result}
    return {"worker_credential_id": result}


@router.put("/{worker_credential_id}")
def update_worker_credential_view(
    worker_credential_id: int, worker_credential: WorkerCredential, db: Session = Depends(get_db)
):
    result = update_worker_credential(db, worker_credential_id, worker_credential)
    if isinstance(result, str):
        return {"error": result}
    return {"worker_credential": result}


@router.delete("/{worker_credential_id}")
def delete_cloud_service_view(worker_credential_id: int, db: Session = Depends(get_db)):
    result = delete_worker_credential(db, worker_credential_id)
    if isinstance(result, str):
        return {"error": result}
    return {"worker_credential": f"deleted {result} rows"}
