# postgres/select.py
import time
import psycopg2


def pg_select():
    try:
        conn = psycopg2.connect(
            host="localhost",
            user="user",
            password="password",
            dbname="my_database",
        )
        cursor = conn.cursor()
        start = time.time()
        cursor.execute("SELECT * FROM test_table WHERE value < 500")
        rows = cursor.fetchall()
        end = time.time()
        print(
            f"PostgreSQL SELECT: Znaleziono {len(rows)} wierszy w {end - start:.4f} s"
        )
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()
