from bson.objectid import ObjectId

from app import logger, mongo_instance


def get_edge_device(id="0"):
    edge_devices_collection = mongo_instance.mydb["edge_devices"]
    try:
        id = ObjectId(str(id))
        result = edge_devices_collection.find_one({"_id": ObjectId(id)})
        if result is not None:
            result["_id"] = str(result["_id"])
        return result
    except Exception as e:
        logger.error("exception in get_edge_device")
        logger.error(e)
        return None


def get_all_edge_device():
    edge_devices_collection = mongo_instance.mydb["edge_devices"]
    mongo_all_edge_devices = list(edge_devices_collection.find({}))
    for i in mongo_all_edge_devices:
        i["_id"] = str(i["_id"])
    all_edge_devices = mongo_all_edge_devices
    return all_edge_devices


def new_edge_device(edge_device: dict):
    edge_devices_collection = mongo_instance.mydb["edge_devices"]
    new_edge_device_obj = edge_devices_collection.insert_one(edge_device)
    return str(new_edge_device_obj.inserted_id)


def update_edge_device(_id, edge_device: dict):
    edge_devices_collection = mongo_instance.mydb["edge_devices"]
    try:
        _id = ObjectId(str(_id))
        update_edge_device_obj = edge_devices_collection.update_one({"_id": ObjectId(_id)}, {"$set": edge_device})
        if update_edge_device_obj is not None:
            if update_edge_device_obj.modified_count > 0:
                return "updated edge_device " + str(_id), update_edge_device_obj.modified_count
            else:
                return "no changes in edge_device unstructured data" + str(_id), 0
        return "error in update edge_device" + str(_id), 0
    except Exception as e:
        logger.error("exception in update_edge_device")
        logger.error(e)
        return "error"


def delete_edge_device(id="0"):
    edge_devices_collection = mongo_instance.mydb["edge_devices"]
    try:
        id = ObjectId(str(id))
        result = edge_devices_collection.delete_one({"_id": ObjectId(id)})
        if result is not None:
            if result.deleted_count > 0:
                return "delete edge_device " + str(id)
            else:
                return "not found edge_device " + str(id)
        return "error in delete edge_device" + str(id)
    except Exception as e:
        logger.error("exception in delete_edge_device")
        logger.error(e)
        return "error"


def count(filters={}):
    edge_devices_collection = mongo_instance.mydb["edge_devices"]
    return edge_devices_collection.find(filters).count()


def get_all_trucks(skip: int = 0, limit: int = 10):
    events_collection = mongo_instance.mydb["events"]
    mongo_all_trucks = events_collection.find({"origin.truck_id": {"$exists": True}}).distinct(key="origin.truck_id")
    return mongo_all_trucks[skip:limit]
