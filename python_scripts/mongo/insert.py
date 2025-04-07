# mongo/insert.py
import time
from pymongo import MongoClient
from common import generate_random_data


def mongo_insert(data_size):
    uri = f"mongodb://user:password@localhost:27017/wypozyczalnia?authSource=admin"
    client = MongoClient(uri)
    db = client["wypozyczalnia"]
    collection = db["test_collection"]
    # Czyścimy kolekcję
    collection.delete_many({})
    data = [
        {"name": name, "value": value}
        for name, value in generate_random_data(data_size)
    ]
    start = time.time()
    collection.insert_many(data)
    end = time.time()
    print(f"MongoDB INSERT: Wstawiono {data_size} dokumentów w {end - start:.4f} s")
    client.close()
