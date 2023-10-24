import os
from pathlib import Path

import pymongo
from bson.json_util import loads
from dotenv import load_dotenv

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

myclient = pymongo.MongoClient(os.getenv("MONGO_SERVER"))
mydb = myclient[os.getenv("DATABASE_NAME")]
mydb.authenticate(os.getenv("MONGO_USER"), os.getenv("MONGO_PWD"))

collection = mydb["components"]

JSON_FILE = "/home/anybody/Projects/PiData/MMG_Peru/folpix-api/backup/components.json"
data = loads(open(JSON_FILE, "r").read())
collection.insert_many(data)
