"""
Настройки Django для тестирования с PostgreSQL.
Используется при запуске тестов через pytest.
"""

import os  # noqa: F405

from .settings import *  # noqa: F403


# Переопределяем настройки для тестов
DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
        "TEST": {
            "NAME": "test_payout_db",
        },
    }
}

# Отключаем миграции для ускорения тестов
MIGRATION_MODULES = {
    "auth": None,
    "contenttypes": None,
    "admin": None,
    "sessions": None,
    "payouts": None,
}

# Celery для тестов - синхронное выполнение
CELERY_BROKER_URL = "memory://"
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_RESULT_BACKEND = "cache+memory://"

# Отключаем логирование для тестов
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "handlers": {
        "null": {
            "class": "logging.NullHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["null"],
            "level": "CRITICAL",
            "propagate": False,
        },
        "celery": {
            "handlers": ["null"],
            "level": "CRITICAL",
            "propagate": False,
        },
    },
}

# Отключаем валидацию паролей для тестов
AUTH_PASSWORD_VALIDATORS = []

# Ускоряем тесты
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Отключаем кэширование для тестов
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}
