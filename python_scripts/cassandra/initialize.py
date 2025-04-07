import time
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider


def initialize_cassandra():
    username = "cassandra_user"
    password = "cassandra_password"

    auth_provider = PlainTextAuthProvider(username=username, password=password)
    cluster = Cluster(["127.0.0.1"], auth_provider=auth_provider)
    session = cluster.connect()

    # Utworzenie keyspace'u "wypozyczalnia" jeśli nie istnieje
    session.execute(
        """
        CREATE KEYSPACE IF NOT EXISTS wypozyczalnia 
        WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}
    """
    )

    # Przełączenie na keyspace "wypozyczalnia"
    session.set_keyspace("wypozyczalnia")

    # Lista komend do utworzenia tabel
    table_commands = [
        """CREATE TABLE IF NOT EXISTS klienci (
            id_klienta uuid PRIMARY KEY,
            imie text,
            nazwisko text,
            telefon text,
            data_urodzenia date,
            pesel text,
            adres text,
            kod_pocztowy text,
            miasto text
        )""",
        """CREATE TABLE IF NOT EXISTS pracownicy (
            id_pracownika uuid PRIMARY KEY,
            imie text,
            nazwisko text,
            telefon text,
            data_urodzenia date,
            pesel text,
            adres text,
            kod_pocztowy text,
            miasto text
        )""",
        """CREATE TABLE IF NOT EXISTS typ_nadwozia (
            id_nadwozia uuid PRIMARY KEY,
            rodzaj_nadwozia text
        )""",
        """CREATE TABLE IF NOT EXISTS marki (
            id_marki uuid PRIMARY KEY,
            nazwa text
        )""",
        """CREATE TABLE IF NOT EXISTS modele (
            id_modelu uuid PRIMARY KEY,
            id_marki uuid,
            nazwa text
        )""",
        """CREATE TABLE IF NOT EXISTS pojazdy (
            id_pojazdu uuid PRIMARY KEY,
            id_modelu uuid,
            przebieg float,
            rok_produkcji int,
            kolor_nadwozia text,
            kolor_wnetrza text,
            skrzynia_biegow text,
            paliwo text,
            pojemnosc_silnika float,
            cena_24h float,
            kaucja float,
            moc int,
            id_nadwozia uuid,
            dostepnosc text
        )""",
        """CREATE TABLE IF NOT EXISTS wypozyczenia (
            id_wypozyczenia uuid PRIMARY KEY,
            id_pojazdu uuid,
            id_klienta uuid,
            id_pracownika uuid,
            data_wypozyczenia timestamp,
            data_zwrotu timestamp,
            przebieg_przed float,
            przebieg_po float
        )""",
        """CREATE TABLE IF NOT EXISTS rezerwacje (
            id_rezerwacji uuid PRIMARY KEY,
            id_pojazdu uuid,
            id_klienta uuid,
            id_pracownika uuid,
            data_rezerwacji timestamp,
            data_od timestamp,
            data_do timestamp,
            status_rezerwacji text
        )""",
        """CREATE TABLE IF NOT EXISTS platnosci (
            id_platnosci uuid PRIMARY KEY,
            id_wypozyczenia uuid,
            kwota float,
            typ_platnosci text,
            data_platnosci timestamp,
            opis text
        )""",
        """CREATE TABLE IF NOT EXISTS serwis (
            id_serwisu uuid PRIMARY KEY,
            id_pojazdu uuid,
            data_serwisu date,
            opis text,
            koszt float
        )""",
    ]

    for command in table_commands:
        session.execute(command)

    session.shutdown()
    cluster.shutdown()
