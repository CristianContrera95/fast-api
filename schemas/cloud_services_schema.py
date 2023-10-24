from sqlalchemy import Column, ForeignKey, Integer, String

from app import Base


class CloudServiceSchema(Base):
    __tablename__ = "cloud_service"

    id = Column("id", Integer, autoincrement=True, primary_key=True, index=True)
    organization_id = Column(
        "organization_id", Integer, ForeignKey("organization.id", ondelete="CASCADE"), nullable=False
    )
    cloud_name = Column("cloud_name", String(64), nullable=False)
    resource_name = Column("resource_name", String(255), index=True, nullable=False)
    type = Column("type", String(255), nullable=False)
    url_endpoint = Column("url_endpoint", String(255), nullable=True)


class CloudCredentialSchema(Base):
    __tablename__ = "cloud_credential"

    id = Column("id", Integer, autoincrement=True, primary_key=True, index=True)
    cloud_service_id = Column(
        "cloud_service_id", Integer, ForeignKey("cloud_service.id", ondelete="CASCADE"), nullable=False
    )
    key = Column("key", String(255), nullable=False)
    value = Column("value", String(255), nullable=False)
