FROM python:3.12-slim

WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем uv с указанием версии
RUN curl -LsSf https://github.com/astral-sh/uv/releases/latest/download/uv-installer.sh | sh

# Добавляем uv в PATH
ENV PATH="/root/.local/bin:${PATH}"

# Создаем ARG для передачи переменной сборки
ARG INSTALL_DEV="false"
ENV INSTALL_DEV=${INSTALL_DEV}

# Проверяем установку
RUN uv --version

# Копируем зависимости
COPY pyproject.toml uv.lock* ./

# Устанавливаем зависимости в систему
RUN if [ "$INSTALL_DEV" = "true" ]; then \
      echo "Устанавливаем dev-зависимости..." && \
      uv pip install --system -e '.[dev]'; \
    else \
      echo "Устанавливаем только production-зависимости..." && \
      uv pip install --system .; \
    fi

# Копируем код
COPY . .

# Команда по умолчанию
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]