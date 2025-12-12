.PHONY: help migrate up down test lint format check

help:
	@echo "Доступные команды:"
	@echo "  make up          - Запустить все сервисы"
	@echo "  make down        - Остановить все сервисы"
	@echo "  make migrate     - Применить миграции"
	@echo "  make test        - Запустить тесты"
	@echo "  make test-cov    - Запустить тесты с покрытием"
	@echo "  make lint        - Проверить код с помощью ruff"
	@echo "  make format      - Форматировать код с помощью ruff"

up:
	docker compose up -d --build

down:
	docker compose down

migrate:
	docker compose exec app python manage.py migrate

test:
	docker compose exec app pytest -v

test-cov:
	docker compose exec app pytest --cov=payouts --cov-report=term-missing --cov-report=html

lint:
	docker compose exec app ruff check .

format:
	docker compose exec app ruff format .
