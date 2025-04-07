import uuid
import random
from datetime import datetime, timedelta

from faker import Faker

# Importy dla baz danych
import mysql.connector
import psycopg2
import gevent.monkey

gevent.monkey.patch_all()
from cassandra.io.geventreactor import GeventConnection
from cassandra.cluster import Cluster
from pymongo import MongoClient

fake = Faker("pl_PL")  # używamy polskiej lokalizacji

# Ilość rekordów do wygenerowania – możesz zmodyfikować ilości
NUM_KLIENCI = 10
NUM_PRACOWNICY = 5
NUM_POJAZDY = 10
NUM_WYPOZYCZENIA = 5
NUM_REZERWACJE = 5
NUM_PLATNOSCI = 5
NUM_SERWIS = 5

BODY_TYPES = ["sedan", "hatchback", "SUV", "coupe", "kombi"]
GEARBOXES = ["manualna", "automatyczna"]
FUEL_TYPES = ["benzyna", "diesel", "elektryczny"]

# Zamiast osobnych list marek i modeli – użyjemy słownika odwzorowującego markę → dostępne modele
brand_to_models = {
    "Toyota": ["Corolla", "Camry", "Yaris", "RAV4", "Highlander", "Prius"],
    "Volkswagen": ["Golf", "Passat", "Polo", "Tiguan", "Touareg", "Arteon"],
    "Ford": ["Focus", "Fiesta", "Mustang", "Explorer", "Edge", "Bronco"],
    "BMW": ["3er", "5er", "X5", "X3", "X1", "i8"],
    "Audi": ["A4", "A6", "Q5", "A3", "A8", "TT"],
    "Honda": ["Civic", "Accord", "CR-V", "Fit", "HR-V", "Pilot"],
    "Nissan": ["Sentra", "Altima", "Qashqai", "Maxima", "Murano", "Leaf"],
    "Mercedes": ["Klasa C", "Klasa E", "Klasa S", "Klasa A", "GLA", "GLE"],
    "Chevrolet": ["Malibu", "Camaro", "Spark", "Impala", "Tahoe", "Equinox"],
    "Hyundai": ["Elantra", "Sonata", "Tucson", "Accent", "Kona", "Santa Fe"],
    "Kia": ["Rio", "Optima", "Sportage", "Soul", "Stinger", "Seltos"],
    "Mazda": ["Mazda3", "Mazda6", "CX-5", "MX-5", "CX-3", "CX-9"],
    "Subaru": ["Impreza", "Forester", "Outback", "BRZ", "Legacy", "WRX"],
}


# --------------------------------------------
# Generowanie danych przykładowych (wspólnych)
# --------------------------------------------


def generate_klienci():
    klienci = []
    for _ in range(NUM_KLIENCI):
        klient = {
            "id_klienta": str(uuid.uuid4()),
            "imie": fake.first_name(),
            "nazwisko": fake.last_name(),
            "telefon": fake.phone_number(),
            "data_urodzenia": fake.date_of_birth(
                minimum_age=18, maximum_age=80
            ).isoformat(),
            "pesel": "".join(str(random.randint(0, 9)) for _ in range(11)),
            "adres": fake.street_address(),
            "kod_pocztowy": fake.postcode(),
            "miasto": fake.city(),
        }
        klienci.append(klient)
    return klienci


def generate_pracownicy():
    pracownicy = []
    for _ in range(NUM_PRACOWNICY):
        pracownik = {
            "id_pracownika": str(uuid.uuid4()),
            "imie": fake.first_name(),
            "nazwisko": fake.last_name(),
            "telefon": fake.phone_number(),
            "email": fake.email(),
        }
        pracownicy.append(pracownik)
    return pracownicy


def generate_typ_nadwozia():
    # Unikalne typy nadwozia
    typy = []
    for typ in set(BODY_TYPES):
        typy.append({"id": str(uuid.uuid4()), "rodzaj_nadwozia": typ})
    return typy


def generate_marki_modele():
    """
    Tworzymy listę marek i listę modeli tak, aby każdy model był przypisany do
    konkretnej marki. Zamiast losowania marek czy modeli z Faker, używamy
    z góry zdefiniowanego słownika brand_to_models.
    """
    marki = []
    modele = []
    for brand, models_list in brand_to_models.items():
        marka_id = str(uuid.uuid4())
        # Tworzymy obiekt reprezentujący markę
        marki.append({"_id": marka_id, "nazwa": brand})
        # Dla każdej z marek tworzymy powiązane modele
        for model_name in models_list:
            model_id = str(uuid.uuid4())
            modele.append({"_id": model_id, "id_marki": marka_id, "nazwa": model_name})
    return marki, modele


def generate_pojazdy(modele):
    """
    Generujemy pojazdy, przy czym każdy pojazd losowo wybiera z dostępnej listy modeli.
    Marka zostanie przypisana dopiero w assign_marka_model, na podstawie id_modelu.
    """
    pojazdy = []
    for _ in range(NUM_POJAZDY):
        model = random.choice(modele)
        pojazd = {
            "id_pojazdu": str(uuid.uuid4()),
            "id_modelu": model["_id"],
            "przebieg": round(random.uniform(10000, 200000), 2),
            "rok_produkcji": random.randint(2000, 2023),
            "kolor_nadwozia": fake.color_name(),
            "kolor_wnetrza": fake.color_name(),
            "skrzynia_biegow": random.choice(GEARBOXES),
            "paliwo": random.choice(FUEL_TYPES),
            "pojemnosc_silnika": round(random.uniform(1.0, 5.0), 1),
            "cena_24h": round(random.uniform(50, 300), 2),
            "kaucja": round(random.uniform(100, 1000), 2),
            "moc": random.randint(70, 400),
            "typ_nadwozia": random.choice(BODY_TYPES),
            "dostepnosc": random.choice(["dostępny", "niedostępny"]),
        }
        pojazdy.append(pojazd)
    return pojazdy


def generate_wypozyczenia(klienci, pojazdy, pracownicy):
    wypozyczenia = []
    for _ in range(NUM_WYPOZYCZENIA):
        klient = random.choice(klienci)
        pojazd = random.choice(pojazdy)
        pracownik = random.choice(pracownicy)
        start_date = fake.date_time_between(start_date="-1y", end_date="now")
        end_date = start_date + timedelta(days=random.randint(1, 14))
        wypozyczenie = {
            "id_wypozyczenia": str(uuid.uuid4()),
            "klient": {
                "id_klienta": klient["id_klienta"],
                "imie": klient["imie"],
                "nazwisko": klient["nazwisko"],
                "telefon": klient["telefon"],
                "pesel": klient["pesel"],
            },
            "pojazd": {
                "id_pojazdu": pojazd["id_pojazdu"],
                "marka": None,  # uzupełniane później
                "model": None,
                "przebieg": pojazd["przebieg"],
            },
            "pracownik": {
                "id_pracownika": pracownik["id_pracownika"],
                "imie": pracownik["imie"],
                "nazwisko": pracownik["nazwisko"],
            },
            "data_wypozyczenia": start_date.isoformat(),
            "data_zwrotu": end_date.isoformat(),
            "przebieg_przed": pojazd["przebieg"],
            "przebieg_po": pojazd["przebieg"] + random.uniform(100, 1000),
        }
        wypozyczenia.append(wypozyczenie)
    return wypozyczenia


def generate_rezerwacje(klienci, pojazdy, pracownicy):
    rezerwacje = []
    for _ in range(NUM_REZERWACJE):
        klient = random.choice(klienci)
        pojazd = random.choice(pojazdy)
        pracownik = random.choice(pracownicy)
        rezerwacja = {
            "id_rezerwacji": str(uuid.uuid4()),
            "klient": {
                "id_klienta": klient["id_klienta"],
                "imie": klient["imie"],
                "nazwisko": klient["nazwisko"],
            },
            "pojazd": {
                "id_pojazdu": pojazd["id_pojazdu"],
                "marka": None,
                "model": None,
            },
            "pracownik": {
                "id_pracownika": pracownik["id_pracownika"],
                "imie": pracownik["imie"],
                "nazwisko": pracownik["nazwisko"],
            },
            "data_rezerwacji": fake.date_time_between(
                start_date="-1y", end_date="now"
            ).isoformat(),
            "data_od": fake.date_time_between(
                start_date="now", end_date="+1y"
            ).isoformat(),
            "data_do": fake.date_time_between(
                start_date="now", end_date="+1y"
            ).isoformat(),
            "status_rezerwacji": random.choice(
                ["oczekuje", "zatwierdzona", "odrzucona"]
            ),
        }
        rezerwacje.append(rezerwacja)
    return rezerwacje


def generate_platnosci(wypozyczenia):
    platnosci = []
    for _ in range(NUM_PLATNOSCI):
        wyp = random.choice(wypozyczenia)
        platnosc = {
            "id_platnosci": str(uuid.uuid4()),
            "wypozyczenie": {
                "id_wypozyczenia": wyp["id_wypozyczenia"],
                "klient": {
                    "imie": wyp["klient"]["imie"],
                    "nazwisko": wyp["klient"]["nazwisko"],
                },
                "pojazd": {
                    "marka": wyp["pojazd"]["marka"],
                    "model": wyp["pojazd"]["model"],
                },
                "data_wypozyczenia": wyp["data_wypozyczenia"],
                "data_zwrotu": wyp["data_zwrotu"],
            },
            "kwota": round(random.uniform(50, 1000), 2),
            "typ_platnosci": random.choice(["karta kredytowa", "przelew", "gotówka"]),
            "data_platnosci": fake.date_time_between(
                start_date="-1y", end_date="now"
            ).isoformat(),
            "opis": fake.sentence(nb_words=6),
        }
        platnosci.append(platnosc)
    return platnosci


def generate_serwis(pojazdy):
    serwis = []
    for _ in range(NUM_SERWIS):
        pojazd = random.choice(pojazdy)
        serwis_record = {
            "id_serwisu": str(uuid.uuid4()),
            "pojazd": {
                "id_pojazdu": pojazd["id_pojazdu"],
                "marka": None,
                "model": None,
            },
            "data_serwisu": fake.date_time_between(
                start_date="-1y", end_date="now"
            ).isoformat(),
            "opis": fake.sentence(nb_words=8),
            "koszt": round(random.uniform(100, 1000), 2),
        }
        serwis.append(serwis_record)
    return serwis


def assign_marka_model(pojazdy, modele, marki):
    """
    Na podstawie ID modelu w pojeździe przypisuje do niego
    odpowiednią nazwę marki i modelu (tekstowe).
    """
    # Mapa: marka_id -> nazwa marki
    marki_map = {marka["_id"]: marka["nazwa"] for marka in marki}
    # Mapa: model_id -> (marka_nazwa, model_nazwa)
    modele_map = {}
    for model in modele:
        marka_nazwa = marki_map.get(model["id_marki"], "Nieznana")
        modele_map[model["_id"]] = (marka_nazwa, model["nazwa"])

    for poj in pojazdy:
        brand_model = modele_map.get(poj["id_modelu"], ("Nieznana", "Nieznany"))
        poj["marka"] = brand_model[0]
        poj["model"] = brand_model[1]

    return pojazdy


# -------------------
# Generowanie danych
# -------------------
klienci = generate_klienci()
pracownicy = generate_pracownicy()
typy_nadwozia = generate_typ_nadwozia()

# Nowa funkcja zwracająca listę marek i listę modeli
marki, modele = generate_marki_modele()

pojazdy = generate_pojazdy(modele)
# Uzupełniamy w słowniku pojazdu nazwę marki i model
pojazdy = assign_marka_model(pojazdy, modele, marki)

wypozyczenia = generate_wypozyczenia(klienci, pojazdy, pracownicy)
rezerwacje = generate_rezerwacje(klienci, pojazdy, pracownicy)
platnosci = generate_platnosci(wypozyczenia)
serwis = generate_serwis(pojazdy)

# ------------------------------------------------------
# Funkcje do wstawiania danych do poszczególnych baz
# (pozostają zasadniczo bez zmian)
# ------------------------------------------------------


# ---- MySQL ----
def populate_mysql():
    print("Łączenie z bazą MySQL...")
    conn = mysql.connector.connect(
        host="localhost",
        port=3306,
        user="user",
        password="password",
        database="my_database",
    )
    cursor = conn.cursor()

    # Tworzymy tabele
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS klienci (
          id VARCHAR(36) PRIMARY KEY,
          imie VARCHAR(50),
          nazwisko VARCHAR(50),
          telefon VARCHAR(20),
          data_urodzenia DATE,
          pesel VARCHAR(20),
          adres VARCHAR(255),
          kod_pocztowy VARCHAR(10),
          miasto VARCHAR(50)
        );
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS pracownicy (
          id VARCHAR(36) PRIMARY KEY,
          imie VARCHAR(50),
          nazwisko VARCHAR(50),
          telefon VARCHAR(20),
          email VARCHAR(100)
        );
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS typ_nadwozia (
          id VARCHAR(36) PRIMARY KEY,
          rodzaj_nadwozia VARCHAR(50)
        );
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS marki (
          id VARCHAR(36) PRIMARY KEY,
          nazwa VARCHAR(50)
        );
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS modele (
          id VARCHAR(36) PRIMARY KEY,
          id_marki VARCHAR(36),
          nazwa VARCHAR(50)
        );
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS pojazdy (
          id VARCHAR(36) PRIMARY KEY,
          id_modelu VARCHAR(36),
          przebieg DOUBLE,
          rok_produkcji INT,
          kolor_nadwozia VARCHAR(50),
          kolor_wnetrza VARCHAR(50),
          skrzynia_biegow VARCHAR(50),
          paliwo VARCHAR(50),
          pojemnosc_silnika DOUBLE,
          cena_24h DOUBLE,
          kaucja DOUBLE,
          moc INT,
          typ_nadwozia VARCHAR(50),
          dostepnosc VARCHAR(50)
        );
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS wypozyczenia (
          id VARCHAR(36) PRIMARY KEY,
          data_wypozyczenia DATETIME,
          data_zwrotu DATETIME,
          przebieg_przed DOUBLE,
          przebieg_po DOUBLE,
          id_klienta VARCHAR(36),
          imie_klienta VARCHAR(50),
          nazwisko_klienta VARCHAR(50),
          telefon_klienta VARCHAR(20),
          pesel_klienta VARCHAR(20),
          id_pojazdu VARCHAR(36),
          marka VARCHAR(50),
          model VARCHAR(50),
          przebieg DOUBLE,
          id_pracownika VARCHAR(36),
          imie_pracownika VARCHAR(50),
          nazwisko_pracownika VARCHAR(50)
        );
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS rezerwacje (
          id VARCHAR(36) PRIMARY KEY,
          data_rezerwacji DATETIME,
          data_od DATETIME,
          data_do DATETIME,
          status_rezerwacji VARCHAR(50),
          id_klienta VARCHAR(36),
          imie_klienta VARCHAR(50),
          nazwisko_klienta VARCHAR(50),
          id_pojazdu VARCHAR(36),
          marka VARCHAR(50),
          model VARCHAR(50),
          id_pracownika VARCHAR(36),
          imie_pracownika VARCHAR(50),
          nazwisko_pracownika VARCHAR(50)
        );
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS platnosci (
          id VARCHAR(36) PRIMARY KEY,
          id_wypozyczenia VARCHAR(36),
          klient_imie VARCHAR(50),
          klient_nazwisko VARCHAR(50),
          pojazd_marka VARCHAR(50),
          pojazd_model VARCHAR(50),
          data_wypozyczenia DATETIME,
          data_zwrotu DATETIME,
          kwota DOUBLE,
          typ_platnosci VARCHAR(50),
          data_platnosci DATETIME,
          opis VARCHAR(255)
        );
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS serwis (
          id VARCHAR(36) PRIMARY KEY,
          id_pojazdu VARCHAR(36),
          marka VARCHAR(50),
          model VARCHAR(50),
          data_serwisu DATETIME,
          opis VARCHAR(255),
          koszt DOUBLE
        );
        """
    )

    # Wstawianie danych
    for klient in klienci:
        cursor.execute(
            """
            INSERT INTO klienci (id, imie, nazwisko, telefon, data_urodzenia, pesel, adres, kod_pocztowy, miasto)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                klient["id_klienta"],
                klient["imie"],
                klient["nazwisko"],
                klient["telefon"],
                klient["data_urodzenia"],
                klient["pesel"],
                klient["adres"],
                klient["kod_pocztowy"],
                klient["miasto"],
            ),
        )
    for pracownik in pracownicy:
        cursor.execute(
            """
            INSERT INTO pracownicy (id, imie, nazwisko, telefon, email)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                pracownik["id_pracownika"],
                pracownik["imie"],
                pracownik["nazwisko"],
                pracownik["telefon"],
                pracownik["email"],
            ),
        )
    for typ in typy_nadwozia:
        cursor.execute(
            """
            INSERT INTO typ_nadwozia (id, rodzaj_nadwozia)
            VALUES (%s, %s)
            """,
            (typ["id"], typ["rodzaj_nadwozia"]),
        )
    for marka in marki:
        cursor.execute(
            """
            INSERT INTO marki (id, nazwa)
            VALUES (%s, %s)
            """,
            (marka["_id"], marka["nazwa"]),
        )
    for model in modele:
        cursor.execute(
            """
            INSERT INTO modele (id, id_marki, nazwa)
            VALUES (%s, %s, %s)
            """,
            (model["_id"], model["id_marki"], model["nazwa"]),
        )
    for poj in pojazdy:
        cursor.execute(
            """
            INSERT INTO pojazdy (id, id_modelu, przebieg, rok_produkcji, kolor_nadwozia, kolor_wnetrza,
                                 skrzynia_biegow, paliwo, pojemnosc_silnika, cena_24h, kaucja,
                                 moc, typ_nadwozia, dostepnosc)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                poj["id_pojazdu"],
                poj["id_modelu"],
                poj["przebieg"],
                poj["rok_produkcji"],
                poj["kolor_nadwozia"],
                poj["kolor_wnetrza"],
                poj["skrzynia_biegow"],
                poj["paliwo"],
                poj["pojemnosc_silnika"],
                poj["cena_24h"],
                poj["kaucja"],
                poj["moc"],
                poj["typ_nadwozia"],
                poj["dostepnosc"],
            ),
        )
    for wyp in wypozyczenia:
        cursor.execute(
            """
            INSERT INTO wypozyczenia (
                id, data_wypozyczenia, data_zwrotu,
                przebieg_przed, przebieg_po,
                id_klienta, imie_klienta, nazwisko_klienta,
                telefon_klienta, pesel_klienta,
                id_pojazdu, marka, model, przebieg,
                id_pracownika, imie_pracownika, nazwisko_pracownika
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                wyp["id_wypozyczenia"],
                wyp["data_wypozyczenia"],
                wyp["data_zwrotu"],
                wyp["przebieg_przed"],
                wyp["przebieg_po"],
                wyp["klient"]["id_klienta"],
                wyp["klient"]["imie"],
                wyp["klient"]["nazwisko"],
                wyp["klient"]["telefon"],
                wyp["klient"]["pesel"],
                wyp["pojazd"]["id_pojazdu"],
                wyp["pojazd"]["marka"],
                wyp["pojazd"]["model"],
                wyp["pojazd"]["przebieg"],
                wyp["pracownik"]["id_pracownika"],
                wyp["pracownik"]["imie"],
                wyp["pracownik"]["nazwisko"],
            ),
        )
    for rez in rezerwacje:
        cursor.execute(
            """
            INSERT INTO rezerwacje (
                id, data_rezerwacji, data_od, data_do, status_rezerwacji,
                id_klienta, imie_klienta, nazwisko_klienta,
                id_pojazdu, marka, model,
                id_pracownika, imie_pracownika, nazwisko_pracownika
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                rez["id_rezerwacji"],
                rez["data_rezerwacji"],
                rez["data_od"],
                rez["data_do"],
                rez["status_rezerwacji"],
                rez["klient"]["id_klienta"],
                rez["klient"]["imie"],
                rez["klient"]["nazwisko"],
                rez["pojazd"]["id_pojazdu"],
                rez["pojazd"]["marka"],
                rez["pojazd"]["model"],
                rez["pracownik"]["id_pracownika"],
                rez["pracownik"]["imie"],
                rez["pracownik"]["nazwisko"],
            ),
        )
    for plat in platnosci:
        cursor.execute(
            """
            INSERT INTO platnosci (
                id, id_wypozyczenia,
                klient_imie, klient_nazwisko,
                pojazd_marka, pojazd_model,
                data_wypozyczenia, data_zwrotu,
                kwota, typ_platnosci,
                data_platnosci, opis
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                plat["id_platnosci"],
                plat["wypozyczenie"]["id_wypozyczenia"],
                plat["wypozyczenie"]["klient"]["imie"],
                plat["wypozyczenie"]["klient"]["nazwisko"],
                plat["wypozyczenie"]["pojazd"]["marka"],
                plat["wypozyczenie"]["pojazd"]["model"],
                plat["wypozyczenie"]["data_wypozyczenia"],
                plat["wypozyczenie"]["data_zwrotu"],
                plat["kwota"],
                plat["typ_platnosci"],
                plat["data_platnosci"],
                plat["opis"],
            ),
        )
    for srv in serwis:
        cursor.execute(
            """
            INSERT INTO serwis (
                id, id_pojazdu, marka, model,
                data_serwisu, opis, koszt
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                srv["id_serwisu"],
                srv["pojazd"]["id_pojazdu"],
                srv["pojazd"]["marka"],
                srv["pojazd"]["model"],
                srv["data_serwisu"],
                srv["opis"],
                srv["koszt"],
            ),
        )
    conn.commit()
    cursor.close()
    conn.close()
    print("Dane zostały wstawione do MySQL.")


# ---- PostgreSQL ----
def populate_postgres():
    print("Łączenie z bazą PostgreSQL...")
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="user",
        password="password",
        dbname="my_database",
    )
    cursor = conn.cursor()
    # Tworzymy tabele (podobnie jak dla MySQL)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS klienci (
          id VARCHAR(36) PRIMARY KEY,
          imie VARCHAR(50),
          nazwisko VARCHAR(50),
          telefon VARCHAR(20),
          data_urodzenia DATE,
          pesel VARCHAR(20),
          adres VARCHAR(255),
          kod_pocztowy VARCHAR(10),
          miasto VARCHAR(50)
        );
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS pracownicy (
          id VARCHAR(36) PRIMARY KEY,
          imie VARCHAR(50),
          nazwisko VARCHAR(50),
          telefon VARCHAR(20),
          email VARCHAR(100)
        );
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS typ_nadwozia (
          id VARCHAR(36) PRIMARY KEY,
          rodzaj_nadwozia VARCHAR(50)
        );
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS marki (
          id VARCHAR(36) PRIMARY KEY,
          nazwa VARCHAR(50)
        );
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS modele (
          id VARCHAR(36) PRIMARY KEY,
          id_marki VARCHAR(36),
          nazwa VARCHAR(50)
        );
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS pojazdy (
          id VARCHAR(36) PRIMARY KEY,
          id_modelu VARCHAR(36),
          przebieg DOUBLE PRECISION,
          rok_produkcji INT,
          kolor_nadwozia VARCHAR(50),
          kolor_wnetrza VARCHAR(50),
          skrzynia_biegow VARCHAR(50),
          paliwo VARCHAR(50),
          pojemnosc_silnika DOUBLE PRECISION,
          cena_24h DOUBLE PRECISION,
          kaucja DOUBLE PRECISION,
          moc INT,
          typ_nadwozia VARCHAR(50),
          dostepnosc VARCHAR(50)
        );
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS wypozyczenia (
          id VARCHAR(36) PRIMARY KEY,
          data_wypozyczenia TIMESTAMP,
          data_zwrotu TIMESTAMP,
          przebieg_przed DOUBLE PRECISION,
          przebieg_po DOUBLE PRECISION,
          id_klienta VARCHAR(36),
          imie_klienta VARCHAR(50),
          nazwisko_klienta VARCHAR(50),
          telefon_klienta VARCHAR(20),
          pesel_klienta VARCHAR(20),
          id_pojazdu VARCHAR(36),
          marka VARCHAR(50),
          model VARCHAR(50),
          przebieg DOUBLE PRECISION,
          id_pracownika VARCHAR(36),
          imie_pracownika VARCHAR(50),
          nazwisko_pracownika VARCHAR(50)
        );
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS rezerwacje (
          id VARCHAR(36) PRIMARY KEY,
          data_rezerwacji TIMESTAMP,
          data_od TIMESTAMP,
          data_do TIMESTAMP,
          status_rezerwacji VARCHAR(50),
          id_klienta VARCHAR(36),
          imie_klienta VARCHAR(50),
          nazwisko_klienta VARCHAR(50),
          id_pojazdu VARCHAR(36),
          marka VARCHAR(50),
          model VARCHAR(50),
          id_pracownika VARCHAR(36),
          imie_pracownika VARCHAR(50),
          nazwisko_pracownika VARCHAR(50)
        );
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS platnosci (
          id VARCHAR(36) PRIMARY KEY,
          id_wypozyczenia VARCHAR(36),
          klient_imie VARCHAR(50),
          klient_nazwisko VARCHAR(50),
          pojazd_marka VARCHAR(50),
          pojazd_model VARCHAR(50),
          data_wypozyczenia TIMESTAMP,
          data_zwrotu TIMESTAMP,
          kwota DOUBLE PRECISION,
          typ_platnosci VARCHAR(50),
          data_platnosci TIMESTAMP,
          opis VARCHAR(255)
        );
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS serwis (
          id VARCHAR(36) PRIMARY KEY,
          id_pojazdu VARCHAR(36),
          marka VARCHAR(50),
          model VARCHAR(50),
          data_serwisu TIMESTAMP,
          opis VARCHAR(255),
          koszt DOUBLE PRECISION
        );
        """
    )
    conn.commit()

    # Wstawianie danych – analogicznie do MySQL
    for klient in klienci:
        cursor.execute(
            """
            INSERT INTO klienci (id, imie, nazwisko, telefon, data_urodzenia, pesel, adres, kod_pocztowy, miasto)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                klient["id_klienta"],
                klient["imie"],
                klient["nazwisko"],
                klient["telefon"],
                klient["data_urodzenia"],
                klient["pesel"],
                klient["adres"],
                klient["kod_pocztowy"],
                klient["miasto"],
            ),
        )
    for pracownik in pracownicy:
        cursor.execute(
            """
            INSERT INTO pracownicy (id, imie, nazwisko, telefon, email)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                pracownik["id_pracownika"],
                pracownik["imie"],
                pracownik["nazwisko"],
                pracownik["telefon"],
                pracownik["email"],
            ),
        )
    for typ in typy_nadwozia:
        cursor.execute(
            """
            INSERT INTO typ_nadwozia (id, rodzaj_nadwozia)
            VALUES (%s, %s)
            """,
            (typ["id"], typ["rodzaj_nadwozia"]),
        )
    for marka in marki:
        cursor.execute(
            """
            INSERT INTO marki (id, nazwa)
            VALUES (%s, %s)
            """,
            (marka["_id"], marka["nazwa"]),
        )
    for model in modele:
        cursor.execute(
            """
            INSERT INTO modele (id, id_marki, nazwa)
            VALUES (%s, %s, %s)
            """,
            (model["_id"], model["id_marki"], model["nazwa"]),
        )
    for poj in pojazdy:
        cursor.execute(
            """
            INSERT INTO pojazdy (id, id_modelu, przebieg, rok_produkcji, kolor_nadwozia, kolor_wnetrza,
                                 skrzynia_biegow, paliwo, pojemnosc_silnika, cena_24h, kaucja, moc,
                                 typ_nadwozia, dostepnosc)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                poj["id_pojazdu"],
                poj["id_modelu"],
                poj["przebieg"],
                poj["rok_produkcji"],
                poj["kolor_nadwozia"],
                poj["kolor_wnetrza"],
                poj["skrzynia_biegow"],
                poj["paliwo"],
                poj["pojemnosc_silnika"],
                poj["cena_24h"],
                poj["kaucja"],
                poj["moc"],
                poj["typ_nadwozia"],
                poj["dostepnosc"],
            ),
        )
    for wyp in wypozyczenia:
        cursor.execute(
            """
            INSERT INTO wypozyczenia (
                id, data_wypozyczenia, data_zwrotu,
                przebieg_przed, przebieg_po,
                id_klienta, imie_klienta, nazwisko_klienta,
                telefon_klienta, pesel_klienta,
                id_pojazdu, marka, model, przebieg,
                id_pracownika, imie_pracownika, nazwisko_pracownika
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                wyp["id_wypozyczenia"],
                wyp["data_wypozyczenia"],
                wyp["data_zwrotu"],
                wyp["przebieg_przed"],
                wyp["przebieg_po"],
                wyp["klient"]["id_klienta"],
                wyp["klient"]["imie"],
                wyp["klient"]["nazwisko"],
                wyp["klient"]["telefon"],
                wyp["klient"]["pesel"],
                wyp["pojazd"]["id_pojazdu"],
                wyp["pojazd"]["marka"],
                wyp["pojazd"]["model"],
                wyp["pojazd"]["przebieg"],
                wyp["pracownik"]["id_pracownika"],
                wyp["pracownik"]["imie"],
                wyp["pracownik"]["nazwisko"],
            ),
        )
    for rez in rezerwacje:
        cursor.execute(
            """
            INSERT INTO rezerwacje (
                id, data_rezerwacji, data_od, data_do, status_rezerwacji,
                id_klienta, imie_klienta, nazwisko_klienta,
                id_pojazdu, marka, model,
                id_pracownika, imie_pracownika, nazwisko_pracownika
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                rez["id_rezerwacji"],
                rez["data_rezerwacji"],
                rez["data_od"],
                rez["data_do"],
                rez["status_rezerwacji"],
                rez["klient"]["id_klienta"],
                rez["klient"]["imie"],
                rez["klient"]["nazwisko"],
                rez["pojazd"]["id_pojazdu"],
                rez["pojazd"]["marka"],
                rez["pojazd"]["model"],
                rez["pracownik"]["id_pracownika"],
                rez["pracownik"]["imie"],
                rez["pracownik"]["nazwisko"],
            ),
        )
    for plat in platnosci:
        cursor.execute(
            """
            INSERT INTO platnosci (
                id, id_wypozyczenia, klient_imie, klient_nazwisko,
                pojazd_marka, pojazd_model,
                data_wypozyczenia, data_zwrotu,
                kwota, typ_platnosci,
                data_platnosci, opis
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                plat["id_platnosci"],
                plat["wypozyczenie"]["id_wypozyczenia"],
                plat["wypozyczenie"]["klient"]["imie"],
                plat["wypozyczenie"]["klient"]["nazwisko"],
                plat["wypozyczenie"]["pojazd"]["marka"],
                plat["wypozyczenie"]["pojazd"]["model"],
                plat["wypozyczenie"]["data_wypozyczenia"],
                plat["wypozyczenie"]["data_zwrotu"],
                plat["kwota"],
                plat["typ_platnosci"],
                plat["data_platnosci"],
                plat["opis"],
            ),
        )
    for srv in serwis:
        cursor.execute(
            """
            INSERT INTO serwis (
                id, id_pojazdu, marka, model,
                data_serwisu, opis, koszt
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                srv["id_serwisu"],
                srv["pojazd"]["id_pojazdu"],
                srv["pojazd"]["marka"],
                srv["pojazd"]["model"],
                srv["data_serwisu"],
                srv["opis"],
                srv["koszt"],
            ),
        )
    conn.commit()
    cursor.close()
    conn.close()
    print("Dane zostały wstawione do PostgreSQL.")


# ---- Cassandra ----
def populate_cassandra():
    print("Łączenie z bazą Cassandra...")
    cluster = Cluster(["localhost"], port=9042, connection_class=GeventConnection)
    session = cluster.connect()
    # Tworzymy keyspace i tabele – przykładowe definicje
    session.execute(
        """
        CREATE KEYSPACE IF NOT EXISTS wypozyczalnia
        WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'}
        """
    )
    session.set_keyspace("wypozyczalnia")

    session.execute(
        """
        CREATE TABLE IF NOT EXISTS klienci (
          id uuid PRIMARY KEY,
          imie text,
          nazwisko text,
          telefon text,
          data_urodzenia date,
          pesel text,
          adres text,
          kod_pocztowy text,
          miasto text
        )
        """
    )
    session.execute(
        """
        CREATE TABLE IF NOT EXISTS pracownicy (
          id uuid PRIMARY KEY,
          imie text,
          nazwisko text,
          telefon text,
          email text
        )
        """
    )
    session.execute(
        """
        CREATE TABLE IF NOT EXISTS marki (
          id uuid PRIMARY KEY,
          nazwa text
        )
        """
    )
    session.execute(
        """
        CREATE TABLE IF NOT EXISTS modele (
          id uuid PRIMARY KEY,
          id_marki uuid,
          nazwa text
        )
        """
    )
    session.execute(
        """
        CREATE TABLE IF NOT EXISTS pojazdy (
          id uuid PRIMARY KEY,
          id_modelu uuid,
          przebieg double,
          rok_produkcji int,
          kolor_nadwozia text,
          kolor_wnetrza text,
          skrzynia_biegow text,
          paliwo text,
          pojemnosc_silnika double,
          cena_24h double,
          kaucja double,
          moc int,
          typ_nadwozia text,
          dostepnosc text
        )
        """
    )
    session.execute(
        """
        CREATE TABLE IF NOT EXISTS wypozyczenia (
          id uuid PRIMARY KEY,
          data_wypozyczenia timestamp,
          data_zwrotu timestamp,
          przebieg_przed double,
          przebieg_po double,
          id_klienta uuid,
          imie_klienta text,
          nazwisko_klienta text,
          telefon_klienta text,
          pesel_klienta text,
          id_pojazdu uuid,
          marka text,
          model text,
          przebieg double,
          id_pracownika uuid,
          imie_pracownika text,
          nazwisko_pracownika text
        )
        """
    )
    session.execute(
        """
        CREATE TABLE IF NOT EXISTS rezerwacje (
          id uuid PRIMARY KEY,
          data_rezerwacji timestamp,
          data_od timestamp,
          data_do timestamp,
          status_rezerwacji text,
          id_klienta uuid,
          imie_klienta text,
          nazwisko_klienta text,
          id_pojazdu uuid,
          marka text,
          model text,
          id_pracownika uuid,
          imie_pracownika text,
          nazwisko_pracownika text
        )
        """
    )
    session.execute(
        """
        CREATE TABLE IF NOT EXISTS platnosci (
          id uuid PRIMARY KEY,
          id_wypozyczenia uuid,
          klient_imie text,
          klient_nazwisko text,
          pojazd_marka text,
          pojazd_model text,
          data_wypozyczenia timestamp,
          data_zwrotu timestamp,
          kwota double,
          typ_platnosci text,
          data_platnosci timestamp,
          opis text
        )
        """
    )
    session.execute(
        """
        CREATE TABLE IF NOT EXISTS serwis (
          id uuid PRIMARY KEY,
          id_pojazdu uuid,
          marka text,
          model text,
          data_serwisu timestamp,
          opis text,
          koszt double
        )
        """
    )

    def uuid_from_str(id_str):
        return uuid.UUID(id_str)

    # Wstawianie danych
    for klient in klienci:
        session.execute(
            """
            INSERT INTO klienci (id, imie, nazwisko, telefon, data_urodzenia, pesel, adres, kod_pocztowy, miasto)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                uuid_from_str(klient["id_klienta"]),
                klient["imie"],
                klient["nazwisko"],
                klient["telefon"],
                datetime.fromisoformat(klient["data_urodzenia"]).date(),
                klient["pesel"],
                klient["adres"],
                klient["kod_pocztowy"],
                klient["miasto"],
            ),
        )
    for pracownik in pracownicy:
        session.execute(
            """
            INSERT INTO pracownicy (id, imie, nazwisko, telefon, email)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                uuid_from_str(pracownik["id_pracownika"]),
                pracownik["imie"],
                pracownik["nazwisko"],
                pracownik["telefon"],
                pracownik["email"],
            ),
        )
    for marka in marki:
        session.execute(
            """
            INSERT INTO marki (id, nazwa)
            VALUES (%s, %s)
            """,
            (uuid_from_str(marka["_id"]), marka["nazwa"]),
        )
    for model in modele:
        session.execute(
            """
            INSERT INTO modele (id, id_marki, nazwa)
            VALUES (%s, %s, %s)
            """,
            (
                uuid_from_str(model["_id"]),
                uuid_from_str(model["id_marki"]),
                model["nazwa"],
            ),
        )
    for poj in pojazdy:
        session.execute(
            """
            INSERT INTO pojazdy (
                id, id_modelu, przebieg, rok_produkcji,
                kolor_nadwozia, kolor_wnetrza,
                skrzynia_biegow, paliwo,
                pojemnosc_silnika, cena_24h,
                kaucja, moc, typ_nadwozia, dostepnosc
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                uuid_from_str(poj["id_pojazdu"]),
                uuid_from_str(poj["id_modelu"]),
                poj["przebieg"],
                poj["rok_produkcji"],
                poj["kolor_nadwozia"],
                poj["kolor_wnetrza"],
                poj["skrzynia_biegow"],
                poj["paliwo"],
                poj["pojemnosc_silnika"],
                poj["cena_24h"],
                poj["kaucja"],
                poj["moc"],
                poj["typ_nadwozia"],
                poj["dostepnosc"],
            ),
        )
    for wyp in wypozyczenia:
        session.execute(
            """
            INSERT INTO wypozyczenia (
                id, data_wypozyczenia, data_zwrotu,
                przebieg_przed, przebieg_po,
                id_klienta, imie_klienta, nazwisko_klienta,
                telefon_klienta, pesel_klienta,
                id_pojazdu, marka, model, przebieg,
                id_pracownika, imie_pracownika, nazwisko_pracownika
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                uuid_from_str(wyp["id_wypozyczenia"]),
                datetime.fromisoformat(wyp["data_wypozyczenia"]),
                datetime.fromisoformat(wyp["data_zwrotu"]),
                wyp["przebieg_przed"],
                wyp["przebieg_po"],
                uuid_from_str(wyp["klient"]["id_klienta"]),
                wyp["klient"]["imie"],
                wyp["klient"]["nazwisko"],
                wyp["klient"]["telefon"],
                wyp["klient"]["pesel"],
                uuid_from_str(wyp["pojazd"]["id_pojazdu"]),
                wyp["pojazd"]["marka"],
                wyp["pojazd"]["model"],
                wyp["pojazd"]["przebieg"],
                uuid_from_str(wyp["pracownik"]["id_pracownika"]),
                wyp["pracownik"]["imie"],
                wyp["pracownik"]["nazwisko"],
            ),
        )
    for rez in rezerwacje:
        session.execute(
            """
            INSERT INTO rezerwacje (
                id, data_rezerwacji, data_od, data_do, status_rezerwacji,
                id_klienta, imie_klienta, nazwisko_klienta,
                id_pojazdu, marka, model,
                id_pracownika, imie_pracownika, nazwisko_pracownika
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                uuid_from_str(rez["id_rezerwacji"]),
                datetime.fromisoformat(rez["data_rezerwacji"]),
                datetime.fromisoformat(rez["data_od"]),
                datetime.fromisoformat(rez["data_do"]),
                rez["status_rezerwacji"],
                uuid_from_str(rez["klient"]["id_klienta"]),
                rez["klient"]["imie"],
                rez["klient"]["nazwisko"],
                uuid_from_str(rez["pojazd"]["id_pojazdu"]),
                rez["pojazd"]["marka"],
                rez["pojazd"]["model"],
                uuid_from_str(rez["pracownik"]["id_pracownika"]),
                rez["pracownik"]["imie"],
                rez["pracownik"]["nazwisko"],
            ),
        )
    for plat in platnosci:
        session.execute(
            """
            INSERT INTO platnosci (
                id, id_wypozyczenia, klient_imie, klient_nazwisko,
                pojazd_marka, pojazd_model,
                data_wypozyczenia, data_zwrotu,
                kwota, typ_platnosci, data_platnosci, opis
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                uuid_from_str(plat["id_platnosci"]),
                uuid_from_str(plat["wypozyczenie"]["id_wypozyczenia"]),
                plat["wypozyczenie"]["klient"]["imie"],
                plat["wypozyczenie"]["klient"]["nazwisko"],
                plat["wypozyczenie"]["pojazd"]["marka"],
                plat["wypozyczenie"]["pojazd"]["model"],
                datetime.fromisoformat(plat["wypozyczenie"]["data_wypozyczenia"]),
                datetime.fromisoformat(plat["wypozyczenie"]["data_zwrotu"]),
                plat["kwota"],
                plat["typ_platnosci"],
                datetime.fromisoformat(plat["data_platnosci"]),
                plat["opis"],
            ),
        )
    for srv in serwis:
        session.execute(
            """
            INSERT INTO serwis (
                id, id_pojazdu, marka, model,
                data_serwisu, opis, koszt
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                uuid_from_str(srv["id_serwisu"]),
                uuid_from_str(srv["pojazd"]["id_pojazdu"]),
                srv["pojazd"]["marka"],
                srv["pojazd"]["model"],
                datetime.fromisoformat(srv["data_serwisu"]),
                srv["opis"],
                srv["koszt"],
            ),
        )

    print("Dane zostały wstawione do Cassandry.")
    session.shutdown()
    cluster.shutdown()


# ---- MongoDB ----
def populate_mongo():
    print("Łączenie z bazą MongoDB...")
    client = MongoClient("mongodb://user:password@localhost:27017/")
    db = client["wypozyczalnia"]
    # Kolekcje – tworzymy lub pobieramy
    collections = {
        "klienci": db.klienci,
        "pracownicy": db.pracownicy,
        "typ_nadwozia": db.typ_nadwozia,
        "marki": db.marki,
        "modele": db.modele,
        "pojazdy": db.pojazdy,
        "wypozyczenia": db.wypozyczenia,
        "rezerwacje": db.rezerwacje,
        "platnosci": db.platnosci,
        "serwis": db.serwis,
    }
    # Wstawianie dokumentów
    collections["klienci"].insert_many(klienci)
    collections["pracownicy"].insert_many(pracownicy)
    collections["typ_nadwozia"].insert_many(typy_nadwozia)
    collections["marki"].insert_many(marki)
    collections["modele"].insert_many(modele)
    collections["pojazdy"].insert_many(pojazdy)
    collections["wypozyczenia"].insert_many(wypozyczenia)
    collections["rezerwacje"].insert_many(rezerwacje)
    collections["platnosci"].insert_many(platnosci)
    collections["serwis"].insert_many(serwis)

    client.close()
    print("Dane zostały wstawione do MongoDB.")


# -------------------
# Funkcja główna
# -------------------
def main():
    try:
        populate_mysql()
    except Exception as e:
        print("Błąd przy wstawianiu do MySQL:", e)
    try:
        populate_postgres()
    except Exception as e:
        print("Błąd przy wstawianiu do PostgreSQL:", e)
    try:
        populate_cassandra()
    except Exception as e:
        print("Błąd przy wstawianiu do Cassandry:", e)
    try:
        populate_mongo()
    except Exception as e:
        print("Błąd przy wstawianiu do MongoDB:", e)


if __name__ == "__main__":
    main()
