# mysql/update.py
import time
from mysql.connector import connect, Error


def mysql_update():
    try:
        conn = connect(
            host="localhost",
            user="user",
            password="password",
            database="my_database",
        )
        cursor = conn.cursor()
        start = time.time()
        cursor.execute("UPDATE test_table SET value = value + 1 WHERE value < 500")
        conn.commit()
        end = time.time()
        print(f"MySQL UPDATE: Zaktualizowano wiersze w {end - start:.4f} s")
    except Error as e:
        print(e)
    finally:
        cursor.close()
        conn.close()
