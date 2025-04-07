import time
import uuid
import random
import string
from datetime import date, timedelta
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider


# Pomocnicze funkcje do generowania losowych danych
def random_date(start_year=1970, end_year=2000):
    start_date = date(start_year, 1, 1)
    end_date = date(end_year, 12, 31)
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)


def random_string(length=8):
    return "".join(random.choices(string.ascii_letters, k=length))


def random_digits(length=11):
    return "".join(random.choices(string.digits, k=length))


def cassandra_insert(data_size):
    username = "cassandra_user"
    password = "cassandra_password"

    auth_provider = PlainTextAuthProvider(username=username, password=password)
    cluster = Cluster(["127.0.0.1"], auth_provider=auth_provider)
    session = cluster.connect("wypozyczalnia")

    # Przygotowanie statementu dla tabeli klienci
    insert_stmt = session.prepare(
        """
        INSERT INTO klienci (
            id_klienta, imie, nazwisko, telefon, data_urodzenia,
            pesel, adres, kod_pocztowy, miasto
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    )

    start = time.time()
    for _ in range(data_size):
        id_klienta = uuid.uuid4()
        imie = random_string(6)
        nazwisko = random_string(8)
        telefon = random_digits(9)
        data_urodzenia = random_date()
        pesel = random_digits(11)
        adres = random_string(12)
        kod_pocztowy = f"{random.randint(10,99)}-{random.randint(100,999)}"
        miasto = random_string(10)
        session.execute(
            insert_stmt,
            (
                id_klienta,
                imie,
                nazwisko,
                telefon,
                data_urodzenia,
                pesel,
                adres,
                kod_pocztowy,
                miasto,
            ),
        )
    end = time.time()
    print(
        f"Cassandra INSERT: Wstawiono {data_size} wierszy do tabeli 'klienci' w {end - start:.4f} s"
    )
    session.shutdown()
    cluster.shutdown()
