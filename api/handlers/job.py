from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy.orm import Session

from api.auth import auth
from api.auth.auth import validate_worker
from api.handlers.common import CommonQueryParams
from app.sqlserverdb import get_db
from core import job_core
from core.job_core import get_job_new, new_job, report_error
from models import JobBase, JobError
from models.account_model import Account

router = APIRouter()


class JobFilterParams:
    def __init__(
        self,
        status: Optional[str] = Query(None, description="Optional filter by status"),
        organization_id: int = Query(..., description="ID of organization"),
    ):
        self.status = status
        self.organization_id = organization_id


@router.get("/")
def get_jobs(
    query: CommonQueryParams = Depends(CommonQueryParams),
    filter: JobFilterParams = Depends(JobFilterParams),
    db: Session = Depends(get_db),
    current_account: Account = Depends(auth.get_current_account),
):
    return job_core.get_jobs(db, query_params=query.__dict__, filter_params=filter.__dict__)


@router.get("/take")
def take_job(db: Session = Depends(get_db), params: Optional[str] = None, worker_id=Depends(validate_worker)):
    job, credentials = get_job_new(db, worker_id)
    if isinstance(job, str):
        return {"jobs": None}
    return {"jobs": job, "credentials": credentials}


@router.post("/")
def new_job_view(
    job: JobBase,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_account: Account = Depends(auth.get_current_account),
):
    result = new_job(db, job, current_account, background_tasks)
    if isinstance(result, str):
        return {"error": result}
    return {"job_id": result}


@router.post("/error")
def report_error_job(job_error: JobError, db: Session = Depends(get_db), worker_id=Depends(validate_worker)):
    result = report_error(db, job_error, worker_id)
    if isinstance(result, str):
        return {"error": result}
    return {"jobs": result}
