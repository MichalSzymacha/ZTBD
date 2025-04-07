import time
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider


def cassandra_delete():
    username = "cassandra_user"
    password = "cassandra_password"

    auth_provider = PlainTextAuthProvider(username=username, password=password)
    cluster = Cluster(["127.0.0.1"], auth_provider=auth_provider)
    session = cluster.connect("wypozyczalnia")

    # Wybieramy identyfikatory klientów spełniających warunek
    rows = list(
        session.execute(
            "SELECT id_klienta FROM klienci WHERE imie < 'M' ALLOW FILTERING"
        )
    )
    start = time.time()
    delete_stmt = session.prepare("DELETE FROM klienci WHERE id_klienta = ?")
    for row in rows[:10]:
        session.execute(delete_stmt, (row.id_klienta,))
    end = time.time()
    print(
        f"Cassandra DELETE: Usunięto 10 wierszy z tabeli 'klienci' w {end - start:.4f} s"
    )

    session.shutdown()
    cluster.shutdown()
