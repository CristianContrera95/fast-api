# @TODO
from bson import ObjectId

from app import logger, mongo_instance

COMPONENTS_COLLECTION_NAME = "components"


def new_component(component: dict):
    components_collection = mongo_instance.mydb[COMPONENTS_COLLECTION_NAME]
    component = components_collection.insert_one(component)
    return str(component.inserted_id)


def get_component(id="0"):
    components_collection = mongo_instance.mydb[COMPONENTS_COLLECTION_NAME]
    try:
        id = ObjectId(str(id))
        result = components_collection.find_one({"_id": id})
        if result is not None:
            result["_id"] = str(result["_id"])
        return result
    except Exception as e:
        logger.error("exception in get_component")
        logger.error(e)
        return None
