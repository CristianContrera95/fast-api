import logging
from datetime import datetime

from sqlalchemy.orm import Session

from app.sqlserverdb import SessionLocal
from core.utils.query_params import exclude_none_keys
from core.utils.virtual_machine_manager import wake_up_worker
from db.sql.cloud_service_sql import get_cloud_credential_by_key, get_cloud_service_by_organization_id
from db.sql.utils import (
    create_record,
    get_count,
    get_record_by_id,
    get_record_by_status,
    get_records,
    update_record_by_id,
)
from models import StatusJob, job_model
from schemas import JobSchema

logger = logging.getLogger(__name__)


def get_jobs(db: Session, query_params: dict = {}, filter_params: dict = {}):
    limit = query_params.get("limit")
    skip = query_params.get("skip")
    return {
        "jobs": get_records(
            db, skip=skip, limit=limit, table_schema=JobSchema, filters=exclude_none_keys(filter_params)
        ),
        "pagination": {
            "total_rows": get_count(db, table_schema=JobSchema, filters=exclude_none_keys(filter_params)),
            "skip": skip,
            "limit": limit,
        },
    }


def get_job_new(db: Session, worker_id):
    jobs_ongoing = get_records(
        db, table_schema=JobSchema, filters={"worker_name": worker_id, "status": StatusJob.Ongoing}
    )
    for job in jobs_ongoing:
        change_to_error_job(job.id, "Worker applied for another new job")

    # @TODO: use transactions
    job_data = get_record_by_status(db, StatusJob.New, JobSchema)
    if job_data is None:
        return "No new jobs", None

    credentials = get_job_credentials(db, job_data.organization_id)

    job_data.status = StatusJob.Ongoing
    job_data.worker_name = worker_id
    update_record_by_id(db, job_data.id, job_data.__dict__, JobSchema)

    return job_data, credentials


def change_to_error_job(job_id, details, end_time=datetime.now()):
    db = SessionLocal()
    job_data = get_record_by_id(db, job_id, JobSchema)
    if job_data is None:
        return False  # "not found job"

    job_data.status = StatusJob.Error
    job_data.details = details
    job_data.end_date = end_time
    update_record_by_id(db, job_data.id, job_data.__dict__, JobSchema)

    return True


def report_error(db: Session, job_error, worker_id, end_time=datetime.now()):
    job_data = get_record_by_id(db, job_error.job_id, JobSchema)
    if job_data is None:
        return "Job not found"  # "not found job"

    if job_data.worker_name != worker_id:
        return "It's not the worker's job"
    if job_data.status == StatusJob.Done:
        return "Job is done"

    job_data.status = StatusJob.Error
    job_data.details = job_error.details
    job_data.end_date = end_time
    update_record_by_id(db, job_data.id, job_data.__dict__, JobSchema)

    return True


def done_job(job_id, worker_id, end_time=datetime.now()):
    db = SessionLocal()
    job_data = get_record_by_id(db, job_id, JobSchema)
    if job_data is None:
        return False  # "not found job"

    job_data.status = StatusJob.Done
    job_data.worker_name = worker_id
    job_data.end_date = end_time
    update_record_by_id(db, job_data.id, job_data.__dict__, JobSchema)

    return True


def get_job_credentials(db, organization_id):
    credentials = {}

    cloud_service = get_cloud_service_by_organization_id(db, organization_id)

    if cloud_service is None:
        raise Exception("cloud service not found")

    if cloud_service.cloud_name == "Azure":
        try:
            storage_account_name = get_cloud_credential_by_key(db, cloud_service.id, "AZURE_KEY_STORAGE_ACCOUNT_NAME")
            storage_account_key = get_cloud_credential_by_key(db, cloud_service.id, "AZURE_KEY_STORAGE_ACCOUNT_KEY")
            container_worker_name = get_cloud_credential_by_key(db, cloud_service.id, "CONTAINER_WORKER_NAME")
        except Exception:
            raise Exception("Error in find name or key to Azure")
        if storage_account_name is not None and storage_account_key is not None:
            credentials = {
                "STORAGE": "Azure",
                "AZURE_KEY_STORAGE_ACCOUNT_NAME": storage_account_name.value,
                "AZURE_KEY_STORAGE_ACCOUNT_KEY": storage_account_key.value,
                "CONTAINER_WORKER_NAME": container_worker_name.value,
            }
        else:
            raise Exception("Storage name or key not found in credentials to Azure")
    elif cloud_service.cloud_name == "S3":
        raise Exception("Not implemented S3")
    else:
        raise Exception("Not implemented " + cloud_service.cloud_name)
    return credentials


def new_job(db: Session, new_job: job_model, current_account, task_queue):
    logger.info("Creating job.")
    new_job_schema = JobSchema(**new_job.dict(exclude_unset=True))

    new_job_schema.status = StatusJob.New
    new_job_schema.organization_id = current_account.organization_id
    logger.info("Saving job.")
    new_job_id = create_record(db, new_job_schema)
    if new_job_id == 0:
        return "error, can't add job"

    logger.info("Waking up worker")
    task_queue.add_task(wake_up_worker)

    logger.info("Returning new job id")
    return new_job_id
