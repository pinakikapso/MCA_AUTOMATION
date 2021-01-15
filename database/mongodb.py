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
    def delete(self):
        self.records.delete_many({})
    def _insert(self,data):
        if self.records.find_one({'CIN':data['CIN']}):
            print(f" Data for {data['CIN']} is available")
        else:
            self.records.insert(data)


    