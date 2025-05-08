import pymysql
import psycopg2
from cassandra.cluster import Cluster
from pymongo import MongoClient
import time
from datetime import datetime
import uuid
import csv
import os

RESULTS_CSV = "benchmark_results.csv"


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

# ------------------ MySQL ------------------
def mysql_queries(num_inserts):
    conn = pymysql.connect(
        host="localhost",
        port=3306,
        user="user",
        password="password",
        database="my_database"
    )
    cursor = conn.cursor()

    @log_time("MySQL GROUP BY 1")
    def group_by_1():
        cursor.execute("""
            SELECT mo.nazwa AS model, COUNT(*) as ilosc
            FROM pojazdy p
            JOIN modele mo ON p.id_modelu = mo.id
            GROUP BY mo.nazwa
            HAVING COUNT(*) > 1
        """)
        cursor.fetchall()

    @log_time("MySQL GROUP BY 2")
    def group_by_2():
        cursor.execute("""
            SELECT skrzynia_biegow, AVG(cena_24h) as srednia
            FROM pojazdy
            GROUP BY skrzynia_biegow
            HAVING AVG(cena_24h) > 100
        """)
        cursor.fetchall()

    @log_time("MySQL GROUP BY 3")
    def group_by_3():
        cursor.execute("""
            SELECT paliwo, COUNT(*)
            FROM pojazdy
            GROUP BY paliwo
            HAVING COUNT(*) BETWEEN 2 AND 10
        """)
        cursor.fetchall()

    @log_time("MySQL INSERT")
    def insert():
        for i in range(num_inserts):
            nazwisko = 'DoUsuniecia' if i % 2 == 0 else 'Zostaw'
            cursor.execute(
                """
                INSERT INTO klienci (id, imie, nazwisko, telefon, data_urodzenia, pesel, adres, kod_pocztowy, miasto)
                VALUES (UUID(), 'Test', %s, '123456789', CURDATE(), '12345678901', 'Testowa 1', '00-000', 'Testowo')
                """,
                (nazwisko,)
            )

    @log_time("MySQL UPDATE")
    def update():
        # Aktualizacja telefonu dla rekordów pozostawionych
        cursor.execute(
            """
            UPDATE klienci
            SET telefon = '987654321'
            WHERE nazwisko = 'Zostaw'
            """
        )

    @log_time("MySQL DELETE")
    def delete():
        cursor.execute(
            """
            DELETE FROM klienci
            WHERE nazwisko = 'DoUsuniecia'
            """
        )

    group_by_1()
    group_by_2()
    group_by_3()
    insert()
    update()
    delete()

    conn.commit()
    cursor.close()
    conn.close()

# ------------------ PostgreSQL ------------------
def postgres_queries(num_inserts):
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="user",
        password="password",
        dbname="my_database"
    )
    cursor = conn.cursor()

    @log_time("PostgreSQL GROUP BY 1")
    def group_by_1():
        cursor.execute("""
            SELECT mo.nazwa AS model, COUNT(*)
            FROM pojazdy p
            JOIN modele mo ON p.id_modelu = mo.id
            GROUP BY mo.nazwa
            HAVING COUNT(*) > 1
        """)
        cursor.fetchall()

    @log_time("PostgreSQL GROUP BY 2")
    def group_by_2():
        cursor.execute("""
            SELECT skrzynia_biegow, AVG(cena_24h)
            FROM pojazdy
            GROUP BY skrzynia_biegow
            HAVING AVG(cena_24h) > 100
        """)
        cursor.fetchall()

    @log_time("PostgreSQL GROUP BY 3")
    def group_by_3():
        cursor.execute("""
            SELECT paliwo, COUNT(*)
            FROM pojazdy
            GROUP BY paliwo
            HAVING COUNT(*) BETWEEN 2 AND 10
        """)
        cursor.fetchall()

    @log_time("PostgreSQL INSERT")
    def insert():
        for i in range(num_inserts):
            nazwisko = 'DoUsuniecia' if i % 2 == 0 else 'Zostaw'
            cursor.execute(
                """
                INSERT INTO klienci (id, imie, nazwisko, telefon, data_urodzenia, pesel, adres, kod_pocztowy, miasto)
                VALUES (gen_random_uuid()::text, 'Test', %s, '123456789', CURRENT_DATE, '12345678901', 'Testowa 1', '00-000', 'Testowo')
                """,
                (nazwisko,)
            )

    @log_time("PostgreSQL UPDATE")
    def update():
        # Aktualizacja kodu pocztowego dla klientów pozostawionych
        cursor.execute(
            """
            UPDATE klienci
            SET kod_pocztowy = '99-999'
            WHERE nazwisko = 'Zostaw'
            """
        )

    @log_time("PostgreSQL DELETE")
    def delete():
        cursor.execute("""
            DELETE FROM klienci
            WHERE nazwisko = 'DoUsuniecia'
        """)

    group_by_1()
    group_by_2()
    group_by_3()
    insert()
    update()
    delete()

    conn.commit()
    cursor.close()
    conn.close()

# ------------------ Cassandra ------------------
def cassandra_queries(num_inserts):
    cluster = Cluster(["localhost"], port=9042)
    session = cluster.connect("wypozyczalnia")

    @log_time("Cassandra SELECT 1")
    def select_1():
        rows = session.execute("SELECT skrzynia_biegow FROM pojazdy")
        list(rows)

    @log_time("Cassandra SELECT 2")
    def select_2():
        rows = session.execute("SELECT paliwo FROM pojazdy")
        list(rows)

    @log_time("Cassandra SELECT 3")
    def select_3():
        rows = session.execute("SELECT kolor_nadwozia FROM pojazdy")
        list(rows)

    ids_to_delete = []

    @log_time("Cassandra INSERT")
    def insert():
        nonlocal ids_to_delete
        for i in range(num_inserts):
            id_ = uuid.uuid4()
            nazwisko = 'DoUsuniecia' if i % 2 == 0 else 'Zostaw'
            session.execute(
                """
                INSERT INTO klienci (id, imie, nazwisko, telefon, data_urodzenia, pesel, adres, kod_pocztowy, miasto, email)
                VALUES (%s, %s, %s, %s, toDate(now()), %s, %s, %s, %s, %s)
                """,
                (id_, 'Test', nazwisko, '123456789', '12345678901', 'Testowa 1', '00-000', 'Testowo', 'test@example.com')
            )
            if nazwisko == 'DoUsuniecia':
                ids_to_delete.append(id_)

    @log_time("Cassandra UPDATE")
    def update():
        # Aktualizacja adresu dla wstawionych rekordów
        for id_ in ids_to_delete:
            session.execute(
                "UPDATE klienci SET adres = 'Nowa 2' WHERE id = %s",
                (id_,)
            )

    @log_time("Cassandra DELETE")
    def delete():
        for id_ in ids_to_delete:
            session.execute("DELETE FROM klienci WHERE id = %s", (id_,))

    select_1()
    select_2()
    select_3()
    insert()
    update()
    delete()

    session.shutdown()
    cluster.shutdown()

# ------------------ MongoDB ------------------
def mongo_queries(num_inserts):
    client = MongoClient("mongodb://user:password@localhost:27017/")
    db = client["wypozyczalnia"]

    @log_time("MongoDB AGGREGATE 1")
    def agg_1():
        list(db.pojazdy.aggregate([
            {"$group": {"_id": "$typ_nadwozia", "count": {"$sum": 1}}},
            {"$match": {"count": {"$gt": 1}}}
        ]))

    @log_time("MongoDB AGGREGATE 2")
    def agg_2():
        list(db.pojazdy.aggregate([
            {"$group": {"_id": "$skrzynia_biegow", "avg": {"$avg": "$cena_24h"}}},
            {"$match": {"avg": {"$gt": 100}}}
        ]))

    @log_time("MongoDB AGGREGATE 3")
    def agg_3():
        list(db.pojazdy.aggregate([
            {"$group": {"_id": "$paliwo", "count": {"$sum": 1}}},
            {"$match": {"count": {"$gte": 2, "$lte": 10}}}
        ]))

    @log_time("MongoDB INSERT")
    def insert():
        for i in range(num_inserts):
            nazwisko = 'DoUsuniecia' if i % 2 == 0 else 'Zostaw'
            db.klienci.insert_one({
                "imie": "Test",
                "nazwisko": nazwisko,
                "telefon": "123456789",
                "data_urodzenia": datetime.now(),
                "pesel": "12345678901",
                "adres": "Testowa 1",
                "kod_pocztowy": "00-000",
                "miasto": "Testowo"
            })

    @log_time("MongoDB UPDATE")
    def update():
        # Zmiana miasta dla dokumentów pozostawionych
        db.klienci.update_many(
            {"nazwisko": "Zostaw"},
            {"$set": {"miasto": "ZmienioneMiasto"}}
        )

    @log_time("MongoDB DELETE")
    def delete():
        db.klienci.delete_many({"nazwisko": "DoUsuniecia"})

    agg_1()
    agg_2()
    agg_3()
    insert()
    update()
    delete()
    client.close()

# ------------------ Run All ------------------
def run_all(num_inserts):
    mysql_queries(num_inserts)
    postgres_queries(num_inserts)
    cassandra_queries(num_inserts)
    mongo_queries(num_inserts)

if __name__ == "__main__":
    run_all(100)
