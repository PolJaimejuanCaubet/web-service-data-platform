from fastapi import Depends
from pymongo import MongoClient
from backend.app.config.config import settings as env



def get_MongoClient():
    client = MongoClient(env.MONGO_URI)
    return client

def get_db(client: MongoClient = Depends(get_MongoClient)):
    db = client["client"]
    return db

def get_collection(db = Depends(get_db)):
    collection = db["users"]
    return collection
