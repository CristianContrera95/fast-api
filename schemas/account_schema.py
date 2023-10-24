from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql.functions import current_timestamp

from app import Base


class AccountSchema(Base):
    __tablename__ = "account"

    id = Column("id", String(255), primary_key=True, index=True)
    role_id = Column("role_id", Integer, ForeignKey("role.id", ondelete="CASCADE"), nullable=False)
    organization_id = Column(
        "organization_id", Integer, ForeignKey("organization.id", ondelete="CASCADE"), nullable=False
    )
    username = Column("username", String(64), index=True, unique=True, nullable=False)
    email = Column("email", String(255), unique=True, nullable=False)
    password = Column("password", String(255), nullable=False)
    job_title = Column("job_title", String(255), nullable=True)
    last_update = Column("last_update", DateTime(), server_default=current_timestamp())
