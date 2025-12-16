# Система выплат (Payouts System)

Микросервис для обработки выплат с валидацией реквизитов и интеграцией с Celery.

## Стек технологий

- Python 3.12+
- Django 6.0+
- Django REST Framework
- PostgreSQL
- Celery + Redis (для фоновых задач)
- Pytest (тестирование)
- Makefile (автоматизация задач)

## Установка

1. Клонируйте репозиторий и перейдите в директорию проекта:
```
git clone git@github.com:DmitriiParshin/payout_service.git
cd payout_service
```

2. Запустите проект в Dev режиме:
```
make up-dev
```

3. Запустите тесты:
```
make test
```

4. Запустите линтер и форматтер:
```
make fix
```

5. Остановите проект в Dev режиме:
```
make down-dev
```

6. Создайте .env файл или переименуйте .env.dev в .env и скорректируйте настройки для Prod режима


7. Запустите проект в Prod режиме:
```
make up
```

8. Примените миграции (применяется дополнительная миграция, которая создает получателей для ручного тестирования):
```
make migrate
```

9. Создайте суперпользователя:
```
make create-su
```

10. Остановите проект в Prod режиме:
```
make down
```

## API Эндпоинты (примеры запросов)

**GET /api/recipients/**

Ответ:
```
{
    "count": 5,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": "2acdcd11-0958-4670-98aa-23089d1cbd9d",
            "full_name": "АО \"ГлобалТрейд\"",
            "bank_name": "ВТБ",
            "account_number": "40817810500000000003",
            "inn": "7703000003",
            "kpp": "770301003",
            "bik": "044525187",
            "corr_account": "30101810000000000187"
        },
        {
            "id": "2b7f2ac3-f280-4eef-9bde-8af4bc0f8597",
            "full_name": "ИП Иванов И.П.",
            "bank_name": "Тинькофф Банк",
            "account_number": "40817810000000000002",
            "inn": "7702000002",
            "kpp": "770201002",
            "bik": "044525974",
            "corr_account": "30101810100000000974"
        },
        {
            "id": "ae937339-1833-4606-b73e-473571bd9b7d",
            "full_name": "ИП Сидорова А.В.",
            "bank_name": "Росбанк",
            "account_number": "40817810700000000005",
            "inn": "7705000005",
            "kpp": "770501005",
            "bik": "044526123",
            "corr_account": "30101810500000000123"
        },
        {
            "id": "32a05577-84a4-4e8b-899a-1f6d642ff95e",
            "full_name": "ООО \"МедиаЛайн\"",
            "bank_name": "Альфа-Банк",
            "account_number": "40817810600000000004",
            "inn": "7704000004",
            "kpp": "770401004",
            "bik": "044525593",
            "corr_account": "30101810400000000593"
        },
        {
            "id": "81b4a104-e80c-435d-92f9-21cbfc7bf4e6",
            "full_name": "ООО \"ТехноСфера\"",
            "bank_name": "Сбербанк",
            "account_number": "40817810900000000001",
            "inn": "7701000001",
            "kpp": "770101001",
            "bik": "044525225",
            "corr_account": "30101810400000000225"
        }
    ]
}
```

**POST /api/payouts/**

Тело запроса:
```
{
	"amount": 6542.02,
	"currency": "RUB",
	"recipient_details": "2acdcd11-0958-4670-98aa-23089d1cbd9d"
}
```
Ответ:
```
{
    "id": "e7c6c4e7-a094-466e-86f6-99e6da3426e3",
    "amount": "6542.02",
    "currency": "RUB",
    "recipient_details": {
        "id": "2acdcd11-0958-4670-98aa-23089d1cbd9d",
        "full_name": "АО \"ГлобалТрейд\"",
        "bank_name": "ВТБ",
        "account_number": "40817810500000000003",
        "inn": "7703000003",
        "kpp": "770301003",
        "bik": "044525187",
        "corr_account": "30101810000000000187"
    },
    "status": "pending",
    "description": "",
    "created_at": "2025-12-16T13:39:16.542801+03:00",
    "updated_at": "2025-12-16T13:39:16.542813+03:00",
    "error_message": ""
}
```

## Описание валют:
```
USD = "USD", "Доллар США"
EUR = "EUR", "Евро"
GBP = "GBP", "Фунт стерлингов"
JPY = "JPY", "Японская иена"
CNY = "CNY", "Китайский юань"
CHF = "CHF", "Швейцарский франк"
CAD = "CAD", "Канадский доллар"
AUD = "AUD", "Австралийский доллар"
NZD = "NZD", "Новозеландский доллар"
RUB = "RUB", "Российский рубль"
```

## Описание статусов:
```
PENDING = "pending", "Ожидает обработки"
PROCESSING = "processing", "В обработке"
COMPLETED = "completed", "Выполнена"
FAILED = "failed", "Ошибка"
CANCELLED = "cancelled", "Отменена"
```