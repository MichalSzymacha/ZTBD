// Przełączamy się na bazę "wypozyczalnia"
db = db.getSiblingDB("wypozyczalnia");

// Kolekcja klienci z indeksem unikalnym dla peselu
db.createCollection("klienci");
db.klienci.createIndex({ pesel: 1 }, { unique: true });

// Kolekcja pracownicy z indeksem unikalnym dla peselu
db.createCollection("pracownicy");
db.pracownicy.createIndex({ pesel: 1 }, { unique: true });

// Kolekcja typ_nadwozia
db.createCollection("typ_nadwozia");

// Kolekcja pojazdy
db.createCollection("pojazdy");

// Kolekcja wypozyczenia
db.createCollection("wypozyczenia");

// Kolekcja rezerwacje
db.createCollection("rezerwacje");

// Kolekcja platnosci
db.createCollection("platnosci");

// Kolekcja serwis
db.createCollection("serwis");
