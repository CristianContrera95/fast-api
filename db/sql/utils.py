import logging


def get_record_by_name(db, record_name, table_schema):
    return db.query(table_schema).filter_by(name=record_name).first()


def get_record_by_id(db, record_id, table_schema):
    return db.query(table_schema).filter_by(id=record_id).first()


def get_record_by_status(db, record_status, table_schema):
    return db.query(table_schema).filter_by(status=record_status).first()


def get_records(db, skip=0, limit=0, table_schema=None, filters={}):
    query = db.query(table_schema).filter_by(**filters).order_by(table_schema.id.desc()).offset(skip)
    if limit is not None and limit > 0:
        query = query.limit(limit)
    return query.all()


def get_count(db, table_schema, filters={}):
    return db.query(table_schema).filter_by(**filters).count()


def create_record(db, record_schema, father_table_collection=None):
    """
    add now register to record table, assume record_schema don't exists already
    """
    try:
        if father_table_collection:
            father_table_collection.append(record_schema)
        else:
            db.add(record_schema)
        db.commit()
        db.refresh(record_schema)
        return record_schema.id
    except Exception as ex:
        print(ex)
        logging.info("create record fails", record_schema, exc_info=ex)
        return 0


def update_record_by_id(db, record_id, record_data, table_schema):
    record = get_record_by_id(db, record_id, table_schema)
    if record is not None:
        for attr in record_data.keys():
            value = record_data[attr]
            setattr(record, attr, value)

        db.add(record)
        db.commit()
        db.refresh(record)
        return record


def delete_record_by_id(db, record_id, table_schema):
    result = db.query(table_schema).filter_by(id=record_id).delete()
    if result:
        db.commit()
        return result
