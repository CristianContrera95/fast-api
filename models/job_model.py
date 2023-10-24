from enum import Enum
from typing import Optional

from pydantic import BaseModel

from models.file_storage_type import FileStorageType
from models.use_case_model import UseCaseModel


class StatusJob(str, Enum):
    New = "New"
    Ongoing = "Ongoing"
    Done = "Done"
    Error = "Error"


class JobBase(BaseModel):
    protocol: FileStorageType
    file_name: str
    use_case: UseCaseModel


class JobError(BaseModel):
    job_id: Optional[str] = None
    details: Optional[str] = None


class Job(JobBase):
    class Config:
        extra = "allow"
        orm_mode = True

    id = int
