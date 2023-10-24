from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql.functions import current_timestamp

from app import Base


class WorkerStorageSchema(Base):
    __tablename__ = "worker_storage"

    id = Column("id", Integer, autoincrement=True, primary_key=True, index=True)
    name = Column("name", String(64), nullable=False)
    protocol = Column("protocol", String(255), nullable=False)
    url_endpoint = Column("url_endpoint", String(255), nullable=False)
    file_system = Column("file_system", String(255), nullable=True)


class WorkerCredentialSchema(Base):
    __tablename__ = "worker_credential"

    id = Column("id", Integer, autoincrement=True, primary_key=True, index=True)
    worker_storage_id = Column(
        "worker_storage_id", Integer, ForeignKey("worker_storage.id", ondelete="CASCADE"), nullable=False
    )
    key = Column("key", String(255), nullable=False)
    value = Column("value", String(255), nullable=False)


class WorkerQueueSchema(Base):
    __tablename__ = "worker_queue"

    id = Column("id", Integer, autoincrement=True, primary_key=True, index=True)
    worker_storage_id = Column(
        "worker_storage_id", Integer, ForeignKey("worker_storage.id", ondelete="CASCADE"), nullable=False
    )
    regexp_path = Column("regexp_path", String(128), nullable=False)
    worker_name = Column("worker_name", String(64), nullable=True)
    start_date = Column("start_date", DateTime(), server_default=current_timestamp())
    end_date = Column("end_date", DateTime(), nullable=True)
