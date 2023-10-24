from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from app import Base


class ViewSchema(Base):
    __tablename__ = "view"

    id = Column("id", String(255), primary_key=True, index=True)
    name = Column("title", String(255))
    roles_allowed = relationship("ViewRoleAssociationSchema")
    single_accounts_allowed = relationship("ViewAccountAssociationSchema")
