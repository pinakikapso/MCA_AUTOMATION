from pymongo import MongoClient
import pandas as pd
from decouple import config
class Mongodb(object):
    def __init__(self):
        self.user=config('USER')
        self.password=config('PASSWORD')
        self.database=config('DATABASE')
        self.cluster=config('CLUSTER')
        client=MongoClient('mongodb+srv://'+self.user+':'+self.password+'@'+self.cluster+'.ubduj.mongodb.net/<dbname>?retryWrites=true&w=majority')
        db=client.get_database(self.database)
        self.records=db.mca
    def _get(self,data):
        d=self.records.find_one(data)
        return d

    def _insert(self,data):
        for d in data:
            check=self._get(d)
            if check  is None:
                self.records.insert_one(d)

    