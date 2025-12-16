.PHONY: help up up-dev down migrate create-su test test-cov lint format fix fix-all

help:
	@echo "Доступные команды:"
	@echo "  make up          - Запустить продакшен окружение"
	@echo "  make up-dev      - Запустить dev окружение"
	@echo "  make down        - Остановить все сервисы"
	@echo "  make migrate     - Применить миграции"
	@echo "  make static      - Собрать статику"
	@echo "  make create-su   - Создать суперпользователя"
	@echo "  make test        - Запустить тесты"
	@echo "  make test-cov    - Запустить тесты с покрытием"
	@echo "  make lint        - Проверить код"
	@echo "  make format      - Отформатировать код"
	@echo "  make fix         - Исправить автоматически исправляемые ошибки"
	@echo "  make fix-all     - Исправить все ошибки (включая unsafe)"

up:
	docker compose up -d --build

down:
	docker compose down -v

up-dev:
	docker compose -f docker-compose.dev.yml up -d --build

down-dev:
	docker compose -f docker-compose.dev.yml down -v

migrate:
	docker compose exec web python manage.py migrate

static:
	docker compose exec web python manage.py collectstatic --no-input

create-su:
	docker compose exec web python manage.py create_superuser

test:
	docker compose -f docker-compose.dev.yml exec dev pytest -v

test-cov:
	docker compose exec dev pytest --cov=payouts --cov-report=term-missing --cov-report=html

lint:
	docker compose -f docker-compose.dev.yml exec dev ruff check .

format:
	docker compose -f docker-compose.dev.yml exec dev ruff format .

fix:
	docker compose -f docker-compose.dev.yml exec dev ruff check --fix .

fix-all:
	docker compose -f docker-compose.dev.yml exec dev ruff check --fix --unsafe-fixes .