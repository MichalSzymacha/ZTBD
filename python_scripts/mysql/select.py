# mysql/select.py
import time
from mysql.connector import connect, Error


def mysql_select():
    try:
        conn = connect(
            host="localhost",
            user="user",
            password="password",
            database="my_database",
        )
        cursor = conn.cursor()
        start = time.time()
        cursor.execute("SELECT * FROM test_table WHERE value < 500")
        rows = cursor.fetchall()
        end = time.time()
        print(f"MySQL SELECT: Znaleziono {len(rows)} wierszy w {end - start:.4f} s")
    except Error as e:
        print(e)
    finally:
        cursor.close()
        conn.close()
