#!/bin/bash
set -e

echo "=== Запуск entrypoint ==="

# Ждём PostgreSQL
echo "⏳ Ожидание PostgreSQL..."
until pg_isready -h "$DB_HOST" -p 5432 -U "$DB_USER"; do
  sleep 1
done
echo "PostgreSQL доступен"

# Применяем миграции
echo "Применение миграций..."
python manage.py migrate

# Создаем суперпользователя (без подвисания)
echo "Создание суперпользователя..."
python manage.py create_superuser --noinput

echo "=== Запуск приложения: $@ ==="
exec "$@"