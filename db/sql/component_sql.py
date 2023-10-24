import logging

from schemas.component_schema import ComponentSchema


def get_component_by_id(db, component_id):
    return db.query(ComponentSchema).filter_by(id=component_id).first()


def create_component(db, id, component_schema):
    try:
        component_schema.id = id
        db.add(component_schema)
        db.commit()
        db.refresh(component_schema)
        return component_schema.id
    except Exception as ex:
        logging.info("Create edge device fails", component_schema, exc_info=ex)
        return 0


def exists(db, component_id):
    return db.query(ComponentSchema.id).filter_by(id=component_id).scalar() is not None
