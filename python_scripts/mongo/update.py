# mongo/update.py
import time
from pymongo import MongoClient


def mongo_update():
    uri = f"mongodb://user:password@localhost:27017/wypozyczalnia?authSource=admin"
    client = MongoClient(uri)
    db = client["wypozyczalnia"]
    collection = db["test_collection"]
    rows = list(collection.find({"value": {"$lt": 500}}))
    start = time.time()
    for doc in rows[:10]:
        collection.update_one({"_id": doc["_id"]}, {"$inc": {"value": 1}})
    end = time.time()
    print(f"MongoDB UPDATE: Zaktualizowano 10 dokumentów w {end - start:.4f} s")
    client.close()
