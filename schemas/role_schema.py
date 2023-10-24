from sqlalchemy import Column, Integer, String

from app import Base


class RoleSchema(Base):
    __tablename__ = "role"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    name = Column(String(255), index=True)
