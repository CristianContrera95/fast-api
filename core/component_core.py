from sqlalchemy.orm import Session

from app import logger
from db.mongodb import component_mongo
from db.sql import component_sql
from models import component_model
from schemas.component_schema import ComponentSchema

from .exceptions.entity_not_found_exceptions import EntityNotFoundException
from .modules.modules import ModuleFactory


def get_component_config():
    # @TODO
    # Must check if the user is able to see component configuration and return it.
    return


def new_component(db: Session, component: component_model.Component):
    component_dict = component.dict(exclude_unset=True)
    created_component_id = component_mongo.new_component(component_dict)
    component_schema = ComponentSchema(**{"id": created_component_id, "name": component.name, "type": component.type})
    return component_sql.create_component(db, created_component_id, component_schema)


def generate_component(db: Session, component_id, filters=None):
    component = component_sql.get_component_by_id(db, component_id)
    if component is None:
        logger.error("Component not found in sql db.")
        raise EntityNotFoundException("Component not found.")
    if component_id == "5fb3f5766deb20cfe0839b26":
        print("a")
    component = component_mongo.get_component(component_id)
    if component is None:
        logger.error("Component not found in mongo db.")
        raise EntityNotFoundException("Component not found.")
    use_case = ModuleFactory.create_module(component["use_case"])
    return use_case.generate_component(db, component, filters)
