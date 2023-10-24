from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.sqlserverdb import get_db
from core.worker_core import delete_worker_storage, get_all_worker_storages, new_worker_storage, update_worker_storage
from models import WorkerStorage

router = APIRouter()


@router.get("/")
def get_all_worker_storages_view(db: Session = Depends(get_db), params: Optional[str] = None):
    all_worker_storages = get_all_worker_storages(db)
    if isinstance(all_worker_storages, str):
        return {"error": "worker_storages not found"}
    return {"worker_storages": all_worker_storages}


@router.post("/")
def new_worker_storage_view(worker_storage: WorkerStorage, db: Session = Depends(get_db)):
    result = new_worker_storage(db, worker_storage)
    if isinstance(result, str):
        return {"error": result}
    return {"worker_storage_id": result}


@router.put("/{worker_storage_id}")
def update_worker_storage_view(worker_storage_id: int, worker_storage: WorkerStorage, db: Session = Depends(get_db)):
    result = update_worker_storage(db, worker_storage_id, worker_storage)
    if isinstance(result, str):
        return {"error": result}
    return {"worker_storage": result}


@router.delete("/{worker_storage_id}")
def delete_cloud_service_view(worker_storage_id: int, db: Session = Depends(get_db)):
    result = delete_worker_storage(db, worker_storage_id)
    if isinstance(result, str):
        return {"error": result}
    return {"worker_storage": f"deleted {result} rows"}
