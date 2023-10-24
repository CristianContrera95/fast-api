import logging

from schemas import EdgeDeviceSchema


def get_edge_device_by_id(db, edge_device_id):
    return db.query(EdgeDeviceSchema).filter_by(id=edge_device_id).first()


def create_edge_device(db, id, edge_device_schema):
    try:
        edge_device_schema.id = id
        db.add(edge_device_schema)
        db.commit()
        db.refresh(edge_device_schema)
        return edge_device_schema.id
    except Exception as ex:
        logging.info("Create edge device fails", edge_device_schema, exc_info=ex)
        return 0


def update_edge_device_by_id(db, edege_device_id, edge_device_data):
    edge_device = get_edge_device_by_id(db, edege_device_id)
    if edge_device is not None:
        for attr in edge_device_data.keys():
            value = edge_device_data[attr]
            setattr(edge_device, attr, value)

        db.add(edge_device)
        db.commit()
        db.refresh(edge_device)
        return edge_device
