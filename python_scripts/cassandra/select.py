import time
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider


def cassandra_select():
    username = "cassandra_user"
    password = "cassandra_password"

    auth_provider = PlainTextAuthProvider(username=username, password=password)
    cluster = Cluster(["127.0.0.1"], auth_provider=auth_provider)
    session = cluster.connect("wypozyczalnia")

    start = time.time()
    # Przykładowe zapytanie: wybierz klientów, których imię zaczyna się na literę mniejszą niż 'M'
    query = "SELECT * FROM klienci WHERE imie < 'M' ALLOW FILTERING"
    rows = list(session.execute(query))
    end = time.time()
    print(
        f"Cassandra SELECT: Znaleziono {len(rows)} wierszy z tabeli 'klienci' w {end - start:.4f} s"
    )

    session.shutdown()
    cluster.shutdown()
