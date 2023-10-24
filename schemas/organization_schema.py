from sqlalchemy import Column, ForeignKey, Integer, String

from app import Base


class OrganizationSchema(Base):
    __tablename__ = "organization"

    id = Column("id", Integer, autoincrement=True, primary_key=True, index=True)
    company_id = Column("company_id", Integer, ForeignKey("company.id", ondelete="CASCADE"), nullable=True)
    name = Column("name", String(64), index=True, unique=True, nullable=False)
    description = Column("description", String(255), nullable=True)
    location = Column("location", String(255), nullable=True)
