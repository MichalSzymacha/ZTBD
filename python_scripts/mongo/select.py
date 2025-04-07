# mongo/select.py
import time
from pymongo import MongoClient


def mongo_select():
    uri = f"mongodb://user:password@localhost:27017/wypozyczalnia?authSource=admin"
    client = MongoClient(uri)
    db = client["wypozyczalnia"]
    collection = db["test_collection"]
    start = time.time()
    rows = list(collection.find({"value": {"$lt": 500}}))
    end = time.time()
    print(f"MongoDB SELECT: Znaleziono {len(rows)} dokumentów w {end - start:.4f} s")
    client.close()
