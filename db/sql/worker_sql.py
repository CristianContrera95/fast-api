from schemas import WorkerQueueSchema


def get_worker_info(db, worker_storage_id, table_schema, skip, limit):
    return (
        db.query(table_schema)
        .order_by(table_schema.id.desc())
        .filter_by(worker_storage_id=worker_storage_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_worker_finished_jobs_count(db):
    return db.query(WorkerQueueSchema).filter_by(end_date=None).count()


# def get_worker_jobs(db, filters, offset=None, limit=None):
#     return db.query(WorkerQueueSchema).filter_by(**filters).skip(offset).limit(limit).all()


def get_unfinished_jobs(db, table_schema):
    return db.query()
