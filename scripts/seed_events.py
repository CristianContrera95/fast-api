import os
import random
from datetime import datetime, timedelta

import pymongo
from bson.objectid import ObjectId

# from urllib.parse import quote_plus
# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker

mongo_client = pymongo.MongoClient(os.getenv("MONGO_SERVER"))
mongo_db = mongo_client[os.getenv("DATABASE_NAME")]
mongo_db.authenticate(os.getenv("MONGO_USER"), os.getenv("MONGO_PWD"))
#
# __URI = (
#     f'DRIVER={os.getenv("SQL_DRIVER")};'
#     + f'SERVER={os.getenv("SQL_SERVER")};'
#     + f'DATABASE={os.getenv("SQL_DATABASE")};'
#     + f'UID={os.getenv("SQL_USER")};'
#     + f'PWD={os.getenv("SQL_PASS")}'
# )
#
# __PARAMS = quote_plus(__URI)
# __SQLALCHEMY_DATABASE_URI = "mssql+pyodbc:///?odbc_connect=%s" % __PARAMS
#
# engine = create_engine(__SQLALCHEMY_DATABASE_URI)
#
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#
# Base = declarative_base()

EVENTS_COUNT = 100
FRAME_COUNT = 500

start_date = datetime.now() - timedelta(minutes=2)
end_date = datetime.now()

edge_devices_ids = [
    (ObjectId("6046318dc7edee52abbafc91"), 1),
    (ObjectId("6046318dc7edee52abbafc92"), 2),
    (ObjectId("6046318dc7edee52abbafc93"), 3),
    (ObjectId("6046318dc7edee52abbafc94"), 4),
    (ObjectId("6046318dc7edee52abbafc95"), 5),
    (ObjectId("6046318dc7edee52abbafc96"), 6),
    (ObjectId("6046318dc7edee52abbafc97"), 7),
    (ObjectId("6046318dc7edee52abbafc98"), 8),
    (ObjectId("6046318dc7edee52abbafc99"), 9),
    (ObjectId("6046318dc7edee52abbafc9a"), 10),
]


def check_edge_devices(edge_id):
    if mongo_db["edge_devices"].find_one({"_id": edge_id}) is None:
        mongo_db["edge_devices"].insert_one({"_id": edge_id, "settings": {"fps": 3, "max_restarts": 5}})


def generate_random_time(lower_bound=start_date, upper_bound=end_date):
    time_between_dates = upper_bound - lower_bound
    seconds_between_dates = int(time_between_dates.total_seconds())
    random_number_of_seconds = random.randrange(seconds_between_dates)
    return lower_bound + timedelta(seconds=random_number_of_seconds)


def generate_random_priority():
    return random.choice(["high", "medium", "low"])


def generate_random_behavior():
    return random.choice(["safe", "unsafe", "single_hand", "eating_drinking", "tamper"])


def generate_random_status():
    return random.choice(["ongoing", "ended"])


def chose_random_edge_device():
    return random.choice(edge_devices_ids)


def get_random_frames(events_id):
    storage_urls = [
        "https://folpixeusstorage.blob.core.windows.net/folpix-alerts/02e9cfe4-5cb6-11eb-b8e4-0e91ac6613b1-232ecaf0-2141-49cb-8843-5a859363907a.jpeg",
        "https://folpixeusstorage.blob.core.windows.net/folpix-alerts/05b0edf2-5cb6-11eb-b8e4-0e91ac6613b1-ea47578f-bc19-4739-bc2b-56d05a00e0c7.jpeg",
        "https://folpixeusstorage.blob.core.windows.net/folpix-alerts/095ae220-569c-11eb-b15f-3af9d3dd92b2-1622d718-4c43-4c9c-9022-744d292bf553.jpeg",
        "https://folpixeusstorage.blob.core.windows.net/folpix-alerts/10a60ac4-5cb3-11eb-b8e4-0e91ac6613b1-c0234aae-b80c-4af7-9228-6f4ccfebaaf4.jpeg",
    ]
    frame = {
        "_id": ObjectId(),
        "event_id": str(random.choice(events_id)),
        "storage": random.choice(storage_urls),
        "position": 1,
        "timestamp": datetime.now(),
    }
    return frame


def generate_random_alert():
    event_date = generate_random_time()
    status = generate_random_status()
    edge_device_id, truck_id = chose_random_edge_device()
    check_edge_devices(edge_device_id)
    alert = {
        "category": "driver_safety",
        "event": {"type": "alert", "priority": generate_random_priority()},
        "timestamp": event_date,
        "insert_timestamp": event_date,
        "last_update": event_date,
        "origin": {"edge_device_id": str(edge_device_id), "truck_id": truck_id},
        "payload": {
            "event_start": event_date,
            "event_end": generate_random_time(lower_bound=event_date) if status == "ended" else None,
            "status": status,
            "confidence": 0,
            "behavior": generate_random_behavior(),
        },
    }
    return alert


alerts = [generate_random_alert() for i in range(EVENTS_COUNT)]

inserted_ids = mongo_db["events"].insert_many(alerts).inserted_ids

frames = [get_random_frames(inserted_ids) for _ in range(FRAME_COUNT)]

inserted_ids = mongo_db["frames"].insert_many(frames).inserted_ids

print("done")
