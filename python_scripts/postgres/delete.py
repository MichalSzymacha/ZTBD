# postgres/delete.py
import time
import psycopg2


def pg_delete():
    try:
        conn = psycopg2.connect(
            host="localhost",
            user="user",
            password="password",
            dbname="my_database",
        )
        cursor = conn.cursor()
        start = time.time()
        cursor.execute("DELETE FROM test_table WHERE value < 500")
        conn.commit()
        end = time.time()
        print(f"PostgreSQL DELETE: Usunięto wiersze w {end - start:.4f} s")
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()
