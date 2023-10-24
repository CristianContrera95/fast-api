from bson.objectid import ObjectId

from app import logger, mongo_instance

VIEWS_COLLECTION_NAME = "views"


def get_view(id="0"):
    views_collection = mongo_instance.mydb[VIEWS_COLLECTION_NAME]
    try:
        id = ObjectId(str(id))
        result = views_collection.find_one({"_id": ObjectId(id)})
        if result is not None:
            result["_id"] = str(result["_id"])
        return result
    except Exception as e:
        logger.error(f"exception in get_view: {e}")
        pass


def new_view(view: dict):
    views_collection = mongo_instance.mydb[VIEWS_COLLECTION_NAME]
    new_view = views_collection.insert_one(view)
    return str(new_view.inserted_id)
