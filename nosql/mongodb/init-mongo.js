// Przełączamy się na bazę "wypozyczalnia"
db = db.getSiblingDB("wypozyczalnia");

// Kolekcja klienci – zapisuje pełne dane klienta
db.createCollection("klienci");

// Kolekcja pracownicy – zapisuje pełne dane pracownika
db.createCollection("pracownicy");

// Kolekcja typ_nadwozia – zawiera typy nadwozi
db.createCollection("typ_nadwozia");

// Kolekcja marki – zawiera marki pojazdów
db.createCollection("marki");

// Kolekcja modele – zawiera modele pojazdów, odnosząc się do marek
db.createCollection("modele");

// Kolekcja pojazdy – odnosi się do modelu i osadza typ nadwozia
db.createCollection("pojazdy");

// Kolekcja wypozyczenia – osadza klienta, pojazd i pracownika
db.createCollection("wypozyczenia");

// Kolekcja rezerwacje – osadza klienta, pojazd i pracownika
db.createCollection("rezerwacje");

// Kolekcja platnosci – osadza wypożyczenie
db.createCollection("platnosci");

// Kolekcja serwis – osadza pojazd
db.createCollection("serwis");

// Przykładowe dane
db.marki.insertMany([
    { 
        _id: UUID(),
        nazwa: "Toyota" 
    },
    { 
        _id: UUID(), 
        nazwa: "BMW" 
    },
]);

db.modele.insertMany([
    { 
        _id: UUID(), 
        id_marki: (db.marki.findOne({ nazwa: "Toyota" }))._id, nazwa: "Corolla" 
    },
    { 
        _id: UUID(), 
        id_marki: (db.marki.findOne({ nazwa: "BMW" }))._id, nazwa: "X5" 
    }
]);

db.klienci.insertMany([
    {
        id_klienta: UUID(),
        imie: "Jan",
        nazwisko: "Kowalski",
        telefon: "123456789",
        data_urodzenia: ISODate("1990-05-15"),
        pesel: "12345678901",
        adres: "Warszawa, ul. Przykładowa 1",
        kod_pocztowy: "00-001",
        miasto: "Warszawa",
    },
]);

db.pojazdy.insertMany([
    {
        id_pojazdu: UUID(),
        id_modelu: (db.modele.findOne({ nazwa: "Corolla" }))._id,
        przebieg: 50000.0,
        rok_produkcji: 2020,
        kolor_nadwozia: "biały",
        kolor_wnetrza: "czarny",
        skrzynia_biegow: "automatyczna",
        paliwo: "benzyna",
        pojemnosc_silnika: 1.8,
        cena_24h: 150.0,
        kaucja: 500.0,
        moc: 140,
        typ_nadwozia: { rodzaj_nadwozia: "sedan" },
        dostepnosc: "dostępny",
    },
]);

db.wypozyczenia.insertMany([
    {
        id_wypozyczenia: UUID(),
        klient: {
            id_klienta: UUID(),
            imie: "Jan",
            nazwisko: "Kowalski",
            telefon: "123456789",
            pesel: "12345678901",
        },
        pojazd: {
            id_pojazdu: UUID(),
            marka: "Toyota",
            model: "Corolla",
            przebieg: 50000.0,
        },
        pracownik: {
            id_pracownika: UUID(),
            imie: "Anna",
            nazwisko: "Nowak",
        },
        data_wypozyczenia: ISODate("2024-03-01T09:00:00Z"),
        data_zwrotu: ISODate("2024-03-07T09:00:00Z"),
        przebieg_przed: 50000.0,
        przebieg_po: 50500.0,
    },
]);

db.rezerwacje.insertMany([
    {
        id_rezerwacji: UUID(),
        klient: {
            id_klienta: UUID(),
            imie: "Jan",
            nazwisko: "Kowalski",
        },
        pojazd: {
            id_pojazdu: UUID(),
            marka: "Toyota",
            model: "Corolla",
        },
        pracownik: {
            id_pracownika: UUID(),
            imie: "Anna",
            nazwisko: "Nowak",
        },
        data_rezerwacji: ISODate("2024-03-05T08:00:00Z"),
        data_od: ISODate("2024-03-10T09:00:00Z"),
        data_do: ISODate("2024-03-15T09:00:00Z"),
        status_rezerwacji: "oczekuje",
    },
]);

db.platnosci.insertMany([
    {
        id_platnosci: UUID(),
        wypozyczenie: {
            id_wypozyczenia: UUID(),
            klient: { imie: "Jan", nazwisko: "Kowalski" },
            pojazd: { marka: "Toyota", model: "Corolla" },
            data_wypozyczenia: ISODate("2024-03-01"),
            data_zwrotu: ISODate("2024-03-07"),
        },
        kwota: 500.0,
        typ_platnosci: "karta kredytowa",
        data_platnosci: ISODate("2024-03-08"),
        opis: "Płatność za wypożyczenie auta",
    },
]);

db.serwis.insertMany([
    {
        id_serwisu: UUID(),
        pojazd: {
            id_pojazdu: UUID(),
            marka: "Toyota",
            model: "Corolla",
        },
        data_serwisu: ISODate("2024-02-20"),
        opis: "Wymiana oleju i filtrów",
        koszt: 300.0,
    },
]);

