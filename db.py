import json

from pymongo import MongoClient

#client = MongoClient("mongodb://localhost:27017")
myclient = MongoClient("mongodb://localhost:27017/")

db = myclient.database_sample
#db = client["GFG"]


collection = myclient.sample_collection
#Collection = db["data"]

with open('atributos.json') as f:
    file_data = json.load(f)

if isinstance(file_data, list):
    Collection.insert_many(file_data)  
else:
    Collection.insert_one(file_data)