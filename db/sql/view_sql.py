import logging

from schemas.view_schema import ViewSchema


def get_view_by_id(db, view_id):
    return db.query(ViewSchema).filter_by(id=view_id).first()


def create_view(db, id, view_schema):
    try:
        view_schema.id = id
        db.add(view_schema)
        db.commit()
        db.refresh(view_schema)
        return view_schema.id
    except Exception as ex:
        logging.info("Create view failed", view_schema, exc_info=ex)
        return 0
