from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app import Base


class ViewRoleAssociationSchema(Base):
    __tablename__ = "view_role"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    role_id = Column("role_id", Integer, ForeignKey("role.id", ondelete="CASCADE"))
    organization_id = Column("organization_id", Integer, ForeignKey("organization.id", ondelete="CASCADE"))
    view_id = Column("view_id", String(255), ForeignKey("view.id", ondelete="CASCADE"))
    view = relationship("ViewSchema")
    role = relationship("RoleSchema")


class ViewAccountAssociationSchema(Base):
    __tablename__ = "view_account"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    account_id = Column("account_id", String(255), ForeignKey("account.id", ondelete="CASCADE"))
    view_id = Column("view_id", String(255), ForeignKey("view.id", ondelete="CASCADE"))
    view = relationship("ViewSchema")
    account = relationship("AccountSchema")
