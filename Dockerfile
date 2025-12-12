FROM python:3.12-slim

WORKDIR /app

# Устанавливаем клиент PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
 postgresql-client \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Установка uv
RUN pip install --no-cache-dir uv

# Копируем зависимости
COPY pyproject.toml uv.lock ./

# Устанавливаем зависимости в систему
RUN uv pip install --system .

# Копируем entrypoint отдельно
COPY entrypoint.sh /entrypoint.sh

# Делаем entrypoint исполняемым
RUN chmod +x /entrypoint.sh

# Копируем код
COPY . .

# Точка входа
ENTRYPOINT ["/entrypoint.sh"]

# Команда по умолчанию
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]