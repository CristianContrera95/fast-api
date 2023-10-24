from datetime import datetime

from app import mongo_instance


def new_frame_record(frame_record):
    events_collection = mongo_instance.mydb["frames"]
    frame_record["insert_timestamp"] = datetime.now()
    new_event_obj = events_collection.insert_one(frame_record)
    return str(new_event_obj.inserted_id)
