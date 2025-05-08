import pymysql
import psycopg2
from cassandra.cluster import Cluster
from pymongo import MongoClient
import time
import csv
import os

RESULTS_CSV = "benchmark_update.csv"

def write_result(label, duration):
    file_exists = os.path.isfile(RESULTS_CSV)
    with open(RESULTS_CSV, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Operacja", "Czas (s)"])
        writer.writerow([label, f"{duration:.4f}"])


def log_time(label):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            duration = end - start
            print(f"{label} wykonano w {duration:.4f} sekundy")
            write_result(label, duration)
            return result
        return wrapper
    return decorator

# ------------------ Testy UPDATE ------------------

def mysql_update():
    conn = pymysql.connect(
        host="localhost", port=3306,
        user="user", password="password",
        database="my_database"
    )
    cursor = conn.cursor()

    @log_time("MySQL UPDATE")
    def update():
        cursor.execute(
            """
            UPDATE klienci
            SET telefon = '987654321'
            WHERE nazwisko = 'Zostaw'
            """
        )

    update()
    conn.commit()
    cursor.close()
    conn.close()


def postgres_update():
    conn = psycopg2.connect(
        host="localhost", port=5432,
        user="user", password="password",
        dbname="my_database"
    )
    cursor = conn.cursor()

    @log_time("PostgreSQL UPDATE")
    def update():
        cursor.execute(
            """
            UPDATE klienci
            SET kod_pocztowy = '99-999'
            WHERE nazwisko = 'Zostaw'
            """
        )

    update()
    conn.commit()
    cursor.close()
    conn.close()


def cassandra_update():
    cluster = Cluster(["localhost"], port=9042)
    session = cluster.connect("wypozyczalnia")

    # Pobranie kluczy do aktualizacji
    rows = session.execute(
        "SELECT id FROM klienci WHERE nazwisko='Zostaw' ALLOW FILTERING"
    )
    ids = [row.id for row in rows]

    @log_time("Cassandra UPDATE")
    def update():
        for record_id in ids:
            session.execute(
                "UPDATE klienci SET adres = 'Nowa 2' WHERE id = %s",
                (record_id,)
            )

    update()
    session.shutdown()
    cluster.shutdown()


def mongo_update():
    client = MongoClient("mongodb://user:password@localhost:27017/")
    db = client["wypozyczalnia"]

    @log_time("MongoDB UPDATE")
    def update():
        db.klienci.update_many(
            {"nazwisko": "Zostaw"},
            {"$set": {"miasto": "ZmienioneMiasto"}}
        )

    update()
    client.close()


if __name__ == "__main__":
    mysql_update()
    postgres_update()
    cassandra_update()
    mongo_update()
