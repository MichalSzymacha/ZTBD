-- Utworzenie keyspace'u
CREATE KEYSPACE IF NOT EXISTS wypozyczalnia 
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

USE wypozyczalnia;

-- Tabela klienci
CREATE TABLE IF NOT EXISTS klienci (
    id_klienta uuid PRIMARY KEY,
    imie text,
    nazwisko text,
    telefon text,
    data_urodzenia date,
    pesel text,
    adres text,
    kod_pocztowy text,
    miasto text
);

-- Tabela pracownicy
CREATE TABLE IF NOT EXISTS pracownicy (
    id_pracownika uuid PRIMARY KEY,
    imie text,
    nazwisko text,
    telefon text,
    data_urodzenia date,
    pesel text,
    adres text,
    kod_pocztowy text,
    miasto text
);

-- Tabela typ_nadwozia
CREATE TABLE IF NOT EXISTS typ_nadwozia (
    id_nadwozia uuid PRIMARY KEY,
    rodzaj_nadwozia text
);

-- Tabela pojazdy
CREATE TABLE IF NOT EXISTS pojazdy (
    id_pojazdu uuid PRIMARY KEY,
    marka text,
    model text,
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
);

-- Tabela wypozyczenia
CREATE TABLE IF NOT EXISTS wypozyczenia (
    id_wypozyczenia uuid PRIMARY KEY,
    id_pojazdu uuid,
    id_klienta uuid,
    id_pracownika uuid,
    data_wypozyczenia timestamp,
    data_zwrotu timestamp,
    przebieg_przed float,
    przebieg_po float
);

-- Tabela rezerwacje
CREATE TABLE IF NOT EXISTS rezerwacje (
    id_rezerwacji uuid PRIMARY KEY,
    id_pojazdu uuid,
    id_klienta uuid,
    id_pracownika uuid,
    data_rezerwacji timestamp,
    data_od timestamp,
    data_do timestamp,
    status_rezerwacji text
);

-- Tabela platnosci
CREATE TABLE IF NOT EXISTS platnosci (
    id_platnosci uuid PRIMARY KEY,
    id_wypozyczenia uuid,
    kwota float,
    typ_platnosci text,
    data_platnosci timestamp,
    opis text
);

-- Tabela serwis
CREATE TABLE IF NOT EXISTS serwis (
    id_serwisu uuid PRIMARY KEY,
    id_pojazdu uuid,
    data_serwisu date,
    opis text,
    koszt float
);
