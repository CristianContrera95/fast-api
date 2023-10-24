from datetime import datetime

from sqlalchemy.orm import Session

from app import logger
from db.mongodb import edge_device_mongo
from db.sql import edge_device_sql
from models import edge_device_model
from models.edge_device_model import EdgeDevice
from schemas import EdgeDeviceSchema

from .message_queues import MessageTypes, message_queues


def get_edge_device(db: Session, id="0"):
    # @ TODO Get also info from SQL DB
    edge_device = edge_device_sql.get_edge_device_by_id(db, id)
    if edge_device is None:
        logger.error("error, edge_device not found in sql db")
        return "error, edge_device not found in sql db"

    var_edge_device = edge_device_mongo.get_edge_device(id)
    if var_edge_device is None:
        logger.error("error, edge_device not found")
        return "error, edge_device not found"
    return var_edge_device


def get_all_edge_device():
    # @ TODO Get also info from SQL DB
    var_edge_device = edge_device_mongo.get_all_edge_device()
    if var_edge_device is None:
        logger.error("error, edge_devices not found")
        return "error, edge_devices not found"
    return var_edge_device


def new_edge_device(db: Session, edge_device: edge_device_model.EdgeDevice):
    edge_device_dict_info = edge_device.dict(exclude_unset=True).copy()
    # Create in mongo db
    mongo_data = {}

    for key in ["settings", "sensors"]:
        if key in edge_device_dict_info.keys():
            mongo_data[key] = edge_device_dict_info.pop(key)

    var_edge_device = edge_device_mongo.new_edge_device(mongo_data)
    # Create also in sql db
    edge_device_schema = EdgeDeviceSchema(**edge_device_dict_info)
    edge_device_sql.create_edge_device(db, var_edge_device, edge_device_schema)

    if var_edge_device is None:
        logger.error("error, in create edge_device")
        return "error, in create edge_device"

    # Create edge device message queue
    message_queues.new_message_queue(var_edge_device)

    return var_edge_device


def update_edge_device(db: Session, _id, edge_device: edge_device_model.EdgeDevice):
    edge_device_dict_info = edge_device.dict(exclude_unset=True).copy()

    # Updates in mongo db
    mongo_data = {}

    for key in ["settings", "sensors"]:
        if key in edge_device_dict_info.keys():
            mongo_data[key] = edge_device_dict_info.pop(key)

    old_edge_device = edge_device_mongo.get_edge_device(_id)

    if old_edge_device is None:
        logger.error("error, edge device not found")
        return "error, edge device not found"
    var_edge_device, modified_count = edge_device_mongo.update_edge_device(_id, mongo_data)

    if var_edge_device is None:
        logger.error("error, in update update_edge_device")
        return "error, in update update_edge_device"

    # Manage also updates in sql db
    if len(edge_device_dict_info) > 0:
        edge_device_sql.update_edge_device_by_id(db, _id, edge_device_dict_info)

    # If configuration has changed we should add a message to the edge device.
    if modified_count > 0:
        actual_config = edge_device_mongo.get_edge_device(_id)
        message_queues.put_message(_id, {"type": MessageTypes.configuration_change.value, "new_config": actual_config})

    return var_edge_device


def delete_edge_device(id="0"):
    # @ TODO delete also from SQL DB
    var_edge_device = edge_device_mongo.delete_edge_device(id)
    if var_edge_device is None:
        logger.error("error, edge_device not found")
        return "error, edge_device not found"
    return var_edge_device


def send_status(db: Session, edge_device_id):
    edge_device = edge_device_sql.get_edge_device_by_id(db, edge_device_id)
    if edge_device is None:
        logger.error("error, edge_device not found in sql db")
        return "error, edge_device not found in sql db"
    message_queues.put_message(edge_device_id, {"type": MessageTypes.send_status.value, "extra_info": ""})
    return edge_device_id


def update_last_interaction(db: Session, id="0"):
    updated_data = EdgeDevice(last_interaction=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    edge_device_sql.update_edge_device_by_id(db, id, updated_data.dict())


def get_all_trucks(skip: int = 0, limit: int = 10):
    # @ TODO Get also info from SQL DB
    var_trucks = edge_device_mongo.get_all_trucks(skip, limit)
    if var_trucks is None:
        logger.error("error, trucks not found")
        return "error, trucks not found"
    return var_trucks
