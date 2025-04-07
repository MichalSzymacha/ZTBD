# mysql/delete.py
import time
from mysql.connector import connect, Error


def mysql_delete():
    try:
        conn = connect(
            host="localhost",
            user="user",
            password="password",
            database="my_database",
        )
        cursor = conn.cursor()
        start = time.time()
        cursor.execute("DELETE FROM test_table WHERE value < 500")
        conn.commit()
        end = time.time()
        print(f"MySQL DELETE: Usunięto wiersze w {end - start:.4f} s")
    except Error as e:
        print(e)
    finally:
        cursor.close()
        conn.close()
