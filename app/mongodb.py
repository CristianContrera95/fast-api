import os

import pymongo


class mongo_class:
    myclient = ""
    mydb = ""

    def __init__(self):
        self.myclient = pymongo.MongoClient(os.getenv("MONGO_SERVER"))
        self.mydb = self.myclient[os.getenv("DATABASE_NAME")]
        self.mydb.authenticate(os.getenv("MONGO_USER"), os.getenv("MONGO_PWD"))
