from django.db import migrations

CURRENCIES = [
    {'code': 'USD', 'name': 'Доллар США'},
    {'code': 'EUR', 'name': 'Евро'},
    {'code': 'GBP', 'name': 'Фунт стерлингов'},
    {'code': 'JPY', 'name': 'Японская иена'},
    {'code': 'CNY', 'name': 'Китайский юань'},
    {'code': 'CHF', 'name': 'Швейцарский франк'},
    {'code': 'CAD', 'name': 'Канадский доллар'},
    {'code': 'AUD', 'name': 'Австралийский доллар'},
    {'code': 'NZD', 'name': 'Новозеландский доллар'},
    {'code': 'RUB', 'name': 'Российский рубль'},
]

RECIPIENTS = [
    {
        'full_name': 'ООО "ТехноСфера"',
        'bank_name': 'Сбербанк',
        'account_number': '40817810900000000001',
        'inn': '7701000001',
        'kpp': '770101001',
        'bik': '044525225',
        'corr_account': '30101810400000000225'
    },
    {
        'full_name': 'ИП Иванов И.П.',
        'bank_name': 'Тинькофф Банк',
        'account_number': '40817810000000000002',
        'inn': '7702000002',
        'kpp': '770201002',
        'bik': '044525974',
        'corr_account': '30101810100000000974'
    },
    {
        'full_name': 'АО "ГлобалТрейд"',
        'bank_name': 'ВТБ',
        'account_number': '40817810500000000003',
        'inn': '7703000003',
        'kpp': '770301003',
        'bik': '044525187',
        'corr_account': '30101810000000000187'
    }
]


def add_currencies(apps, schema_editor):
    Currency = apps.get_model('payouts', 'Currency')
    for data in CURRENCIES:
        Currency.objects.get_or_create(**data)


def remove_currencies(apps, schema_editor):
    Currency = apps.get_model('payouts', 'Currency')
    Currency.objects.filter(code__in=[c['code'] for c in CURRENCIES]).delete()


def add_recipient_details(apps, schema_editor):
    RecipientDetails = apps.get_model('payouts', 'RecipientDetails')
    for data in RECIPIENTS:
        RecipientDetails.objects.get_or_create(**data)


def remove_recipient_details(apps, schema_editor):
    RecipientDetails = apps.get_model('payouts', 'RecipientDetails')
    RecipientDetails.objects.filter(inn__in=[r['inn'] for r in RECIPIENTS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('payouts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_currencies, remove_currencies),
        migrations.RunPython(add_recipient_details, remove_recipient_details),
    ]