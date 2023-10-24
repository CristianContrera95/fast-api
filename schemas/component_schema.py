from sqlalchemy import Column, String

from app import Base


class ComponentSchema(Base):
    __tablename__ = "component"

    id = Column("id", String(255), primary_key=True, index=True)
    type = Column("type", String(255))
    name = Column("name", String(255))
    # TODO: unir esto con view (foreign key o tabla de union)
