import time
import random
import string
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider


def random_digits(length=9):
    return "".join(random.choices(string.digits, k=length))


def cassandra_update():
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
    update_stmt = session.prepare("UPDATE klienci SET telefon = ? WHERE id_klienta = ?")
    for row in rows[:10]:
        new_telefon = random_digits(9)
        session.execute(update_stmt, (new_telefon, row.id_klienta))
    end = time.time()
    print(
        f"Cassandra UPDATE: Zaktualizowano 10 wierszy w tabeli 'klienci' w {end - start:.4f} s"
    )

    session.shutdown()
    cluster.shutdown()
