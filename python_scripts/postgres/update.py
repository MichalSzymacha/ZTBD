# postgres/update.py
import time
import psycopg2


def pg_update():
    try:
        conn = psycopg2.connect(
            host="localhost",
            user="user",
            password="password",
            dbname="my_database",
        )
        cursor = conn.cursor()
        start = time.time()
        cursor.execute("UPDATE test_table SET value = value + 1 WHERE value < 500")
        conn.commit()
        end = time.time()
        print(f"PostgreSQL UPDATE: Zaktualizowano wiersze w {end - start:.4f} s")
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()
