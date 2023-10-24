from sqlalchemy import Column, DateTime, String

from app import Base


class EdgeDeviceSchema(Base):
    __tablename__ = "edge_device"

    id = Column("id", String(255), primary_key=True, index=True)
    type = Column("type", String(255), index=True)
    ip = Column("ip", String(255), index=True)
    port = Column("port", String(255), index=True)
    status = Column("status", String(255), index=True)
    last_interaction = Column("last_interaction", DateTime())
    sw_version = Column("sw_version", String(255), index=True)
