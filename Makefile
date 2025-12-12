.PHONY: help up up-dev down migrate test test-cov lint format fix fix-all

help:
	@echo "Доступные команды:"
	@echo "  make up          - Запустить продакшен окружение"
	@echo "  make up-dev      - Запустить dev окружение"
	@echo "  make down        - Остановить все сервисы"
	@echo "  make migrate     - Применить миграции"
	@echo "  make test        - Запустить тесты"
	@echo "  make test-cov    - Запустить тесты с покрытием"
	@echo "  make lint        - Проверить код"
	@echo "  make format      - Отформатировать код"
	@echo "  make fix         - Исправить автоматически исправляемые ошибки"
	@echo "  make fix-all     - Исправить все ошибки (включая unsafe)"

up:
	docker compose up -d --build

up-dev:
	docker compose -f docker-compose.dev.yml up -d --build

down:
	docker compose down

migrate:
	docker compose exec web python manage.py migrate

test:
	docker compose -f docker-compose.dev.yml exec web pytest -v

test-cov:
	docker compose exec web pytest --cov=payouts --cov-report=term-missing --cov-report=html

lint:
	docker compose -f docker-compose.dev.yml exec web ruff check .

# Форматирование
format:
	docker compose -f docker-compose.dev.yml exec web ruff format .

# Автоматическое исправление ошибок
fix:
	docker compose -f docker-compose.dev.yml exec web ruff check --fix .

# Исправление всех ошибок (включая unsafe)
fix-all:
	docker compose -f docker-compose.dev.yml exec web ruff check --fix --unsafe-fixes .