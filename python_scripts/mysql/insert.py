# mysql/insert.py
import time
from mysql.connector import connect, Error
from common import generate_random_data


def mysql_insert(data_size):
    try:
        conn = connect(
            host="localhost",
            user="user",
            password="password",
            database="my_database",
        )
        cursor = conn.cursor()
        # Przygotowanie tabeli
        cursor.execute("DROP TABLE IF EXISTS test_table")
        cursor.execute(
            """
            CREATE TABLE test_table (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50),
                value INT
            )
        """
        )
        conn.commit()
        data = generate_random_data(data_size)
        start = time.time()
        cursor.executemany("INSERT INTO test_table (name, value) VALUES (%s, %s)", data)
        conn.commit()
        end = time.time()
        print(f"MySQL INSERT: Wstawiono {data_size} wierszy w {end - start:.4f} s")
    except Error as e:
        print(e)
    finally:
        cursor.close()
        conn.close()
