from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.sql.functions import current_timestamp

from app import Base
from models.file_storage_type import FileStorageType
from models.job_model import StatusJob


class JobSchema(Base):
    __tablename__ = "job"

    id = Column("id", Integer, autoincrement=True, primary_key=True, index=True)
    use_case = Column("use_case", Enum("driver_safety", "people_counter"), nullable=False)
    organization_id = Column(
        "organization_id", Integer, ForeignKey("organization.id", ondelete="CASCADE"), nullable=False
    )
    protocol = Column("protocol", Enum(FileStorageType), nullable=False)
    file_name = Column("file_name", String(255), nullable=False)
    worker_name = Column("worker_name", String(255), nullable=True)
    status = Column("status", Enum(StatusJob), nullable=False)
    details = Column("details", String(255), nullable=True)
    start_date = Column("start_date", DateTime(), server_default=current_timestamp())
    end_date = Column("end_date", DateTime(), nullable=True)
