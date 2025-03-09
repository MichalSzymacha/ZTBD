CREATE DATABASE IF NOT EXISTS wypozyczalnia;
USE wypozyczalnia;

-- Tabela KLIENCI
CREATE TABLE klienci (
    id_klienta        INT PRIMARY KEY AUTO_INCREMENT,
    imie              VARCHAR(50) NOT NULL,
    nazwisko          VARCHAR(50) NOT NULL,
    telefon           VARCHAR(15),
    data_urodzenia    DATE,
    pesel             BIGINT UNIQUE,
    adres             TEXT,
    kod_pocztowy      VARCHAR(10),
    miasto            TEXT
);

-- Tabela PRACOWNICY
CREATE TABLE pracownicy (
    id_pracownika     INT PRIMARY KEY AUTO_INCREMENT,
    imie              VARCHAR(50) NOT NULL,
    nazwisko          VARCHAR(50) NOT NULL,
    telefon           VARCHAR(15),
    data_urodzenia    DATE,
    pesel             BIGINT UNIQUE,
    adres             TEXT,
    kod_pocztowy      VARCHAR(10),
    miasto            TEXT
);

-- Tabela TYP_NADWOZIA
CREATE TABLE typ_nadwozia (
    id_nadwozia       INT PRIMARY KEY AUTO_INCREMENT,
    rodzaj_nadwozia   TEXT NOT NULL
);

-- Tabela POJAZDY
CREATE TABLE pojazdy (
    id_pojazdu        INT PRIMARY KEY AUTO_INCREMENT,
    marka             TEXT NOT NULL,
    model             TEXT NOT NULL,
    przebieg          FLOAT,
    rok_produkcji     YEAR,
    kolor_nadwozia    TEXT,
    kolor_wnetrza     TEXT,
    skrzynia_biegow   TEXT CHECK (skrzynia_biegow IN ('manualna', 'automatyczna')),
    paliwo            TEXT CHECK (paliwo IN ('benzyna', 'diesel', 'hybryda', 'elektryczny')),
    pojemnosc_silnika FLOAT,
    cena_24h          FLOAT NOT NULL,
    kaucja            FLOAT NOT NULL,
    moc               INT,
    id_nadwozia       INT,
    dostepnosc        VARCHAR(3) CHECK (dostepnosc IN ('tak', 'nie')),
    FOREIGN KEY (id_nadwozia) REFERENCES typ_nadwozia(id_nadwozia)
);

-- Tabela WYPOŻYCZENIA
CREATE TABLE wypozyczenia (
    id_wypozyczenia   INT PRIMARY KEY AUTO_INCREMENT,
    id_pojazdu        INT,
    id_klienta        INT,
    id_pracownika     INT,
    data_wypozyczenia TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_zwrotu       TIMESTAMP NULL,
    przebieg_przed    FLOAT,
    przebieg_po       FLOAT,
    FOREIGN KEY (id_pojazdu) REFERENCES pojazdy(id_pojazdu),
    FOREIGN KEY (id_klienta) REFERENCES klienci(id_klienta),
    FOREIGN KEY (id_pracownika) REFERENCES pracownicy(id_pracownika)
);

-- Tabela REZERWACJE
CREATE TABLE rezerwacje (
    id_rezerwacji     INT PRIMARY KEY AUTO_INCREMENT,
    id_pojazdu        INT,
    id_klienta        INT,
    id_pracownika     INT,
    data_rezerwacji   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_od           TIMESTAMP NOT NULL,
    data_do           TIMESTAMP NOT NULL,
    status_rezerwacji VARCHAR(20) CHECK (status_rezerwacji IN ('oczekująca', 'potwierdzona', 'anulowana')),
    FOREIGN KEY (id_pojazdu) REFERENCES pojazdy(id_pojazdu),
    FOREIGN KEY (id_klienta) REFERENCES klienci(id_klienta),
    FOREIGN KEY (id_pracownika) REFERENCES pracownicy(id_pracownika)
);

-- Tabela PŁATNOŚCI
CREATE TABLE platnosci (
    id_platnosci      INT PRIMARY KEY AUTO_INCREMENT,
    id_wypozyczenia   INT,
    kwota             FLOAT NOT NULL,
    typ_platnosci     VARCHAR(20) CHECK (typ_platnosci IN ('gotowka', 'karta', 'przelew')),
    data_platnosci    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    opis              TEXT,
    FOREIGN KEY (id_wypozyczenia) REFERENCES wypozyczenia(id_wypozyczenia)
);

-- Tabela SERWIS
CREATE TABLE serwis (
    id_serwisu        INT PRIMARY KEY AUTO_INCREMENT,
    id_pojazdu        INT,
    data_serwisu      DATE NOT NULL,
    opis              TEXT NOT NULL,
    koszt             FLOAT NOT NULL,
    FOREIGN KEY (id_pojazdu) REFERENCES pojazdy(id_pojazdu)
);
