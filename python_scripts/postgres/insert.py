# postgres/insert.py
import time
import psycopg2
from common import generate_random_data


def pg_insert(data_size):
    try:
        conn = psycopg2.connect(
            host="localhost",
            user="user",
            password="password",
            dbname="my_database",
        )
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS test_table")
        cursor.execute(
            """
            CREATE TABLE test_table (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50),
                value INT
            )
        """
        )
        conn.commit()
        data = generate_random_data(data_size)
        start = time.time()
        args_str = b",".join(cursor.mogrify("(%s, %s)", x) for x in data)
        cursor.execute(b"INSERT INTO test_table (name, value) VALUES " + args_str)
        conn.commit()
        end = time.time()
        print(f"PostgreSQL INSERT: Wstawiono {data_size} wierszy w {end - start:.4f} s")
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()
