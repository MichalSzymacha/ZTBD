#!/bin/bash

# Dane logowania do PostgreSQL
PG_HOST="postgres"
PG_PORT="5432"
PG_USER="user"
PG_DB="my_database"
PG_PASSWORD="password"

# Czekaj na PostgreSQL (max 30 sekund)
echo "⏳ Oczekiwanie na PostgreSQL..."
for i in {1..15}; do
    if nc -z $PG_HOST $PG_PORT; then
        echo "✅ PostgreSQL jest gotowy!"
        break
    fi
    echo "❌ PostgreSQL jeszcze nie jest gotowy..."
    sleep 2
done

# Jeśli PostgreSQL nadal nie działa po 30 sekundach, zakończ skrypt
if ! nc -z $PG_HOST $PG_PORT; then
    echo "⛔ PostgreSQL nie uruchomił się poprawnie. Sprawdź logi!"
    exit 1
fi


