from sqlalchemy import Column, Integer, String

from app import Base


class CompanySchema(Base):
    __tablename__ = "company"

    id = Column("id", Integer, autoincrement=True, primary_key=True, index=True)
    name = Column("name", String(64), index=True, unique=True, nullable=False)
    type = Column("description", String(255), nullable=True)
