import sys
from datetime import datetime
from enum import Enum
from typing import List, Tuple

import pymongo
from bson.objectid import ObjectId
from pymongo import ReturnDocument

from app import logger, mongo_instance
from core.utils.query_params import SortOrder
from db.mongodb.common import convert_id_field_collection

EVENTS_COLLECTION_NAME = "events"

DURATION_CALCULATED_FIELD = "duration"
EVENTS_DEFAULT_LIMIT = 100

class FieldTranslation:
    def __init__(self, document_field, _type):
        self.document_field = document_field
        self.type = _type


def is_int(s):
    if s[0] in ("-", "+"):
        return s[1:].isdigit()
    return s.isdigit()


def convert_to_mongo_filters(params_dict, query_params):
    mongo_params = []
    valid_params = {k: v for k, v in query_params.items() if k in params_dict}
    for k, v in valid_params.items():
        if params_dict[k].type == ObjectId and ObjectId.is_valid(v):
            mongo_params.append({params_dict[k].document_field: ObjectId(v)})
        elif params_dict[k].type == int and is_int(v):
            mongo_params.append({params_dict[k].document_field: int(v)})
        elif params_dict[k].type == str:
            mongo_params.append({params_dict[k].document_field: {"$exists": True, "$regex": v}})
    return mongo_params


def get_event(id="0"):
    events_collection = mongo_instance.mydb[EVENTS_COLLECTION_NAME]
    try:
        id = ObjectId(str(id))
        result = events_collection.find_one({"_id": ObjectId(id)})
        if result is not None:
            result["_id"] = str(result["_id"])
        return result
    except Exception as e:
        logger.error("exception in get_event")
        logger.error(e)
        pass


def get_all_events(filters={}, offset=0, limit=EVENTS_DEFAULT_LIMIT, sort_fields: List[Tuple[str, SortOrder]] = []):
    events_collection = mongo_instance.mydb[EVENTS_COLLECTION_NAME]

    offset = 0 if not offset else offset
    limit = EVENTS_DEFAULT_LIMIT if not limit else limit

    mongo_filters = __get_mongo_event_filters(filters)

    logger.info(f"Filters inside $match: {mongo_filters}")

    mongo_pipeline = [
        {"$match": mongo_filters},
    ]

    if DURATION_CALCULATED_FIELD in dict(sort_fields):
        mongo_pipeline.extend(
            [
                {
                    "$addFields": {
                        DURATION_CALCULATED_FIELD: {
                            "$divide": [
                                {
                                    "$subtract": [
                                        {"$ifNull": ["$payload.event_end", datetime.utcnow()]},
                                        "$payload.event_start",
                                    ]
                                },
                                60 * 1000 * 60,
                            ]
                        }
                    }
                },
                {"$sort": dict(__parse_sort_parameters(sort_fields))},
            ]
        )

    mongo_pipeline.extend([{"$skip": offset}, {"$limit": limit}])
    mongo_pipeline.extend(
        [{"$lookup": {"from": "frames", "localField": "_id", "foreignField": "event_id", "as": "frames"}}]
    )

    if len(sort_fields) > 0 and DURATION_CALCULATED_FIELD not in dict(sort_fields):
        sort_fields = __parse_sort_parameters(sort_fields)
        sort_pipeline = [
            {"$unwind": "$event"},
            {"$unwind": "$origin"},
            {"$unwind": "$payload"},
            {"$sort": dict(sort_fields)},
        ]
        sort_pipeline.extend(mongo_pipeline)
        mongo_pipeline = sort_pipeline
        logger.info(sort_fields)

    logger.info(mongo_pipeline)
    mongo_all_events = events_collection.aggregate(mongo_pipeline)

    mongo_all_events = list(mongo_all_events)

    convert_id_field_collection(mongo_all_events)

    return mongo_all_events


def __parse_sort_parameters(sort_fields):
    sort_params = {
        "edge_device_id": "origin.edge_device_id",
        "id": "_id",
        "truck_id": "origin.truck_id",
        "behavior": "payload.behavior",
        "priority": "event.priority",
        "timestamp": "timestamp",
        "status": "payload.status",
        "event_start": "payload.event_start",
        DURATION_CALCULATED_FIELD: DURATION_CALCULATED_FIELD,
    }

    sort_fields = [
        (sort_params[a], pymongo.ASCENDING if b == SortOrder.asc else pymongo.DESCENDING) for a, b in sort_fields
    ]

    return sort_fields


def __get_mongo_event_filters(filter_params):
    # Translation of query parameters of URL to MongoDB nested attributes of documents
    and_params = {"event_type": FieldTranslation(document_field="event.type", _type=str)}

    or_params = {
        "edge_device_id": FieldTranslation(document_field="origin.edge_device_id", _type=ObjectId),
        "id": FieldTranslation(document_field="_id", _type=ObjectId),
        "truck_id": FieldTranslation(document_field="origin.truck_id", _type=int),
        "behavior": FieldTranslation(document_field="payload.behavior", _type=str),
        "status": FieldTranslation(document_field="payload.status", _type=str),
        "priority": FieldTranslation(document_field="event.priority", _type=str),
    }

    mongo_filters = {
        "$and": (
                convert_to_mongo_filters(and_params, filter_params)
                + [{"event": {"$exists": True}}, {"origin": {"$exists": True}}, {"payload": {"$exists": True}}]
        )
    }

    or_mongo_filters = convert_to_mongo_filters(or_params, filter_params)

    if or_mongo_filters:
        mongo_filters["$or"] = or_mongo_filters

    return mongo_filters


def get_last_event(filters={}):
    events_collection = mongo_instance.mydb[EVENTS_COLLECTION_NAME]
    return events_collection.find_one(filters, sort=[("_id", 1)])


def new_event(event):
    events_collection = mongo_instance.mydb[EVENTS_COLLECTION_NAME]
    event["insert_timestamp"] = datetime.now()
    new_event_obj = events_collection.insert_one(event)
    return str(new_event_obj.inserted_id)


def update_event(event):
    events_collection = mongo_instance.mydb[EVENTS_COLLECTION_NAME]
    event["last_update"] = datetime.now()
    updated = events_collection.find_one_and_update(
        {"_id": event["_id"]}, {"$set": event}, return_document=ReturnDocument.AFTER
    )
    updated["id"] = str(updated["_id"])
    del updated["_id"]
    return updated


def update_events(query_filters, update_fields):
    events_collection = mongo_instance.mydb[EVENTS_COLLECTION_NAME]
    update_fields["last_update"] = datetime.now()
    events_collection.update_many(query_filters, {"$set": update_fields})


def group_count(group_by_fields, filters, extra_settings=[], further_groupings=[]):
    events_collection = mongo_instance.mydb[EVENTS_COLLECTION_NAME]
    pipeline = [{"$match": filters}]
    pipeline.extend(extra_settings)
    pipeline.append({"$group": {"_id": group_by_fields, "count": {"$sum": 1}}})
    pipeline.extend(further_groupings)
    agg_result = events_collection.aggregate(pipeline)
    groups = list(agg_result)
    return groups


def bucket_count(group_by, hour_limits, filters):
    events_collection = mongo_instance.mydb[EVENTS_COLLECTION_NAME]
    last_bound = sys.maxsize
    bucket_boundaries = hour_limits + [last_bound]
    pipeline = [{"$match": filters}]
    bucket_grouping = {
        "$bucket": {
            "groupBy": group_by,
            "boundaries": bucket_boundaries,
            "default": last_bound,
            "output": {"count": {"$sum": 1}},
        }
    }
    pipeline.append(bucket_grouping)
    agg_result = events_collection.aggregate(pipeline)
    groups = list(agg_result)
    return groups


def count(filters):
    events_collection = mongo_instance.mydb[EVENTS_COLLECTION_NAME]
    mongo_filters = __get_mongo_event_filters(filters)
    return events_collection.count(mongo_filters)


def get_events_by_truck(truck_id: int = 0, sort=True):
    events_collection = mongo_instance.mydb[EVENTS_COLLECTION_NAME]
    events = events_collection.find({"origin.truck_id": truck_id, "payload.behavior": {"$exists": True}})
    if sort:
        return events.sort([("timestamp", pymongo.DESCENDING)])
    return events
