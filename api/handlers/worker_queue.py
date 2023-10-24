from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.sqlserverdb import get_db
from core.worker_core import get_all_worker_queues, new_worker_queue
from models import WorkerQueue

router = APIRouter()


@router.get("/")
def get_all_worker_queues_view(db: Session = Depends(get_db), worker_storage_id: int = 0, params: Optional[str] = None):
    all_worker_queues = get_all_worker_queues(db, worker_storage_id)
    if isinstance(all_worker_queues, str):
        return {"error": "worker_queues not found"}
    return {"worker_queues": all_worker_queues}


@router.post("/")
def new_worker_queue_view(worker_queue: WorkerQueue, db: Session = Depends(get_db)):
    result = new_worker_queue(db, worker_queue)
    if isinstance(result, str):
        return {"error": result}
    return {"worker_queue_id": result}
