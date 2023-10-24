from sqlalchemy.orm import Session

from db.sql.utils import create_record, delete_record_by_id, get_records, update_record_by_id
from db.sql.worker_sql import get_worker_info
from models import WorkerCredential, WorkerQueue, WorkerStorage
from schemas import WorkerCredentialSchema, WorkerQueueSchema, WorkerStorageSchema


def get_all_worker_storages(db: Session, skip: int = 0, limit: int = 100):
    worker_storages = get_records(db, skip, limit, WorkerStorageSchema)
    if worker_storages is None:
        return "error, worker_storages not found"
    return worker_storages


def get_all_worker_credentials(db: Session, worker_storage_id: int, skip: int = 0, limit: int = 100):
    worker_credentials = get_worker_info(db, worker_storage_id, WorkerCredentialSchema, skip, limit)
    if worker_credentials is None:
        return "error, worker_credentials not found"
    return worker_credentials


def get_all_worker_queues(db: Session, worker_storage_id: int, skip: int = 0, limit: int = 100):
    worker_queues = get_worker_info(db, worker_storage_id, WorkerQueueSchema, skip, limit)
    if worker_queues is None:
        return "error, worker_queues not found"
    return worker_queues


def new_worker_storage(db: Session, worker_storage: WorkerStorage):
    worker_storage_schema = WorkerStorageSchema(**worker_storage.dict(exclude_unset=True))

    worker_storage_id = create_record(db, worker_storage_schema)
    if worker_storage_id == 0:
        return "error, can't add worker_storage"
    return worker_storage_id


def new_worker_credential(db: Session, worker_credential: WorkerCredential):
    worker_credential_schema = WorkerCredentialSchema(**worker_credential.dict(exclude_unset=True))

    worker_credential_id = create_record(db, worker_credential_schema)
    if worker_credential_id == 0:
        return "error, can't add worker_credential"
    return worker_credential_id


def new_worker_queue(db: Session, worker_queue: WorkerQueue):
    worker_queue_schema = WorkerQueueSchema(**worker_queue.dict(exclude_unset=True))

    worker_queue_id = create_record(db, worker_queue_schema)
    if worker_queue_id == 0:
        return "error, can't add worker_queue"
    return worker_queue_id


def update_worker_storage(db: Session, worker_storage_id: int, worker_storage: WorkerStorage):
    updated_worker_storage = update_record_by_id(
        db, worker_storage_id, worker_storage.dict(exclude_unset=True), WorkerStorageSchema
    )
    if updated_worker_storage is None:
        return f"error, worker_storage {worker_storage_id} don't exists"
    return updated_worker_storage


def update_worker_credential(db: Session, worker_credential_id: int, worker_credential: WorkerCredential):
    updated_worker_credential = update_record_by_id(
        db, worker_credential_id, worker_credential.dict(exclude_unset=True), WorkerCredentialSchema
    )
    if updated_worker_credential is None:
        return f"error, worker_credential {worker_credential_id} don't exists"
    return updated_worker_credential


def delete_worker_storage(db: Session, worker_storage_id: int):
    result = delete_record_by_id(db, worker_storage_id, WorkerStorageSchema)
    if result is None:
        return f"error, worker_storage_id: {worker_storage_id} don't exists"
    return result


def delete_worker_credential(db: Session, worker_credential_id: int):
    result = delete_record_by_id(db, worker_credential_id, WorkerCredentialSchema)
    if result is None:
        return f"error, worker_storage_id: {worker_credential_id} don't exists"
    return result


# def delete_worker_queue(db: Session, worker_queue_id: int):
#     result = delete_record_by_id(db, worker_queue_id, WorkerQueueSchema)
#     if result is None:
#         return f"error, worker_queue_id: {worker_queue_id} don't exists"
#     return result
