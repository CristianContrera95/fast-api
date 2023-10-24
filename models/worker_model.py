from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# WorkerStorage
class WorkerStorageBase(BaseModel):
    name = str
    protocol = str
    url_endpoint = str
    file_system: Optional[str] = None


class WorkerStorage(WorkerStorageBase):
    class Config:
        extra = "allow"
        orm_mode = True

    id = int


# WorkerCredential
class WorkerCredentialBase(BaseModel):
    worker_storage_id = int
    key = str
    value = str


class WorkerCredential(WorkerCredentialBase):
    class Config:
        extra = "allow"
        orm_mode = True

    id = int


# WorkerQueue
class WorkerQueueBase(BaseModel):
    worker_storage_id = str
    regexp_path = str
    worker_name: Optional[str] = None
    start_date: Optional[datetime] = datetime.now()
    end_date: Optional[datetime] = None


class WorkerQueue(WorkerQueueBase):
    class Config:
        extra = "allow"
        orm_mode = True

    id = int
